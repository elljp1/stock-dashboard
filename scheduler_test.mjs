import {test} from 'node:test';
import assert from 'node:assert/strict';
import worker, {dueSlot, run} from './scheduler-worker.mjs';
const env = {ENABLED:'true', GITHUB_TOKEN:'test-fixture-only'};
const at = s => new Date(s);
test('all requested slots in EDT and EST, with no extra slots', () => {
  const expected=[360,420,480,540,555,560,565,570,575,585];
  for(let m=600;m<=1020;m+=30) expected.push(m);
  expected.push(1080);
  for(const [day,offset] of [['2026-09-09','-04:00'],['2026-12-09','-05:00']]) {
    const seen=[];
    let previous=null;
    for(let m=0;m<1440;m++) {
      const time=day+'T'+String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0')+':00'+offset;
      const slot=dueSlot(at(time));
      if(slot && slot.timestamp!==previous) seen.push(m);
      previous=slot?.timestamp ?? null;
    }
    assert.deepEqual(seen,expected);
  }
});
test('DST transitions and weekends retain only daily review', () => {
  for(const day of ['2026-03-08T18:00:00-04:00','2026-11-01T18:00:00-05:00'])
    assert.equal(dueSlot(at(day)).timestamp, at(day).getTime());
  assert.equal(dueSlot(at('2026-09-12T09:30:00-04:00')),null);
  assert.equal(dueSlot(at('2026-09-12T18:45:00-04:00')).eastern,'2026-09-12 18:00 ET');
});
function upstream({review='2026-09-09T09:12:00-04:00',runs=[],rejectReview=false,dispatchCode=204}={}) {
  const calls=[];
  const fetcher=async (url,opts) => {
    calls.push({url,opts});
    if(url.includes('daily_review')) {
      assert.equal(opts.headers.Authorization,undefined,'credentials only go to GitHub');
      if(rejectReview) throw Error('offline');
      return Response.json({reviewedAt:review});
    }
    if(url.includes('/runs?')) return Response.json({workflow_runs:runs});
    assert.ok(url.endsWith('/dispatches'));
    assert.equal(opts.method,'POST');
    assert.deepEqual(JSON.parse(opts.body),{ref:'main'});
    return new Response(null,{status:dispatchCode});
  };
  return {calls,fetcher};
}
test('fresh publication skips; overdue and unavailable publications dispatch', async () => {
  for(const [config,state] of [[{review:'2026-09-09T09:20:00-04:00'},'current'],[{},'dispatch_accepted'],[{rejectReview:true},'dispatch_accepted']]) {
    const u=upstream(config);
    assert.equal((await run(env,at('2026-09-09T09:20:30-04:00'),u.fetcher)).state,state);
    assert.equal(u.calls.filter(c=>c.opts.method==='POST').length,state==='current'?0:1);
  }
});
test('active builds and recent dispatches suppress duplicates; stuck builds fail visibly', async () => {
  const now=at('2026-09-09T09:25:00-04:00');
  for(const [status,state] of [['in_progress','refresh_in_progress'],['completed','retry_cooldown']]) {
    const u=upstream({runs:[{id:12,status,event:'workflow_dispatch',created_at:'2026-09-09T13:24:00Z'}]});
    assert.equal((await run(env,now,u.fetcher)).state,state);
    assert.equal(u.calls.filter(c=>c.opts.method==='POST').length,0);
  }
  const u=upstream({runs:[{status:'queued',created_at:'2026-09-09T12:00:00Z'}]});
  await assert.rejects(run(env,now,u.fetcher),/stuck/);
});
test('dispatch rejection is never reported as success; disabled service does no work', async () => {
  const u=upstream({dispatchCode:403});
  await assert.rejects(run(env,at('2026-09-09T09:20:00-04:00'),u.fetcher),/HTTP 403/);
  assert.equal((await run({},new Date(),()=>{throw Error('unexpected network');})).state,'disabled');
  await assert.rejects(run({ENABLED:'true'},at('2026-09-09T09:20:00-04:00'),u.fetcher),/Missing/);
});
test('public HTTP requests cannot dispatch a refresh', async () => {
  assert.equal((await worker.fetch(new Request('https://test.invalid/run',{method:'POST'}),env)).status,404);
  assert.equal((await worker.fetch(new Request('https://test.invalid/health'),{})).status,503);
});
