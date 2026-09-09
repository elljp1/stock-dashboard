// Independent clock for the existing validated GitHub refresh/deploy pipeline.
// No public request can dispatch a run; only Cloudflare scheduled events can.
const REVIEW = 'https://elljp1.github.io/stock-dashboard/daily_review.json';
const WORKFLOW = 'https://api.github.com/repos/elljp1/stock-dashboard/actions/workflows/refresh.yml';
const MINUTE = 60000;
const eastern = new Intl.DateTimeFormat('en-US', {
  timeZone:'America/New_York', year:'numeric', month:'2-digit', day:'2-digit',
  hour:'2-digit', minute:'2-digit', hourCycle:'h23', weekday:'short'
});
export function dueSlot(now) {
  const p = Object.fromEntries(eastern.formatToParts(now).map(x => [x.type, x.value]));
  const minute = Number(p.hour)*60 + Number(p.minute);
  // Allow recovery through 19:00 Eastern, including a late daily review.
  if(minute < 360 || minute > 1140) return null;
  const slots = [1080];
  if(!['Sat','Sun'].includes(p.weekday)) {
    slots.push(360,420,480,540,555,560,565,570,575,585);
    for(let t=600;t<=1020;t+=30) slots.push(t);
  }
  const due = slots.filter(t => t <= minute).sort((a,b)=>b-a)[0];
  if(due === undefined) return null;
  // Since all slots are daytime, no offset transition occurs between now/due.
  const timestamp = Math.floor(now.getTime()/MINUTE)*MINUTE - (minute-due)*MINUTE;
  return {timestamp, eastern:`${p.year}-${p.month}-${p.day} ${String(Math.floor(due/60)).padStart(2,'0')}:${String(due%60).padStart(2,'0')} ET`};
}
async function request(fetcher, url, options={}) {
  const response = await fetcher(url, {...options, redirect:'error', signal:AbortSignal.timeout(15000)});
  if(!response.ok) throw new Error(`Upstream HTTP ${response.status}`);
  return response;
}
export async function freshness(now, fetcher=fetch) {
  const due = dueSlot(now);
  if(!due) return {state:'outside_schedule', due:null};
  const response = await request(fetcher, REVIEW+'?check='+now.getTime(), {headers:{'Cache-Control':'no-cache'}});
  const review = await response.json();
  const reviewed = Date.parse(review.reviewedAt);
  if(!Number.isFinite(reviewed) || reviewed > now.getTime()+MINUTE)
    throw new Error('Invalid published review timestamp');
  return {state:reviewed >= due.timestamp ? 'current' : 'overdue', due:due.eastern, reviewedAt:review.reviewedAt};
}
export async function run(env, now=new Date(), fetcher=fetch) {
  if(env.ENABLED !== 'true') return {state:'disabled'};
  if(!dueSlot(now)) return {state:'outside_schedule'};
  if(!env.GITHUB_TOKEN) throw new Error('Missing GITHUB_TOKEN secret');
  let status;
  try { status = await freshness(now, fetcher); }
  catch { status = {state:'freshness_unavailable'}; }
  if(status.state === 'current') return status;
  const headers = {
    Authorization:'Bearer '+env.GITHUB_TOKEN,
    Accept:'application/vnd.github+json',
    'X-GitHub-Api-Version':'2026-03-10',
    'User-Agent':'stock-dashboard-scheduler'
  };
  const response = await request(fetcher, WORKFLOW+'/runs?branch=main&per_page=20', {headers});
  const {workflow_runs:runs} = await response.json();
  if(!Array.isArray(runs)) throw new Error('Invalid workflow response');
  const active = runs.find(r => r.status !== 'completed');
  if(active) {
    const started = Date.parse(active.created_at);
    if(!Number.isFinite(started) || now.getTime()-started > 45*MINUTE)
      throw new Error('Refresh stuck for over 45 minutes; inspect GitHub Actions');
    return {...status, state:'refresh_in_progress', runId:active.id};
  }
  // Allow GitHub's run list and Pages deployment time to settle before retrying.
  const recent = runs.find(r => r.event === 'workflow_dispatch' &&
    now.getTime()-Date.parse(r.created_at) < 3*MINUTE);
  if(recent) return {...status, state:'retry_cooldown', runId:recent.id};
  const dispatched = await request(fetcher, WORKFLOW+'/dispatches', {
    method:'POST', headers:{...headers,'Content-Type':'application/json'}, body:JSON.stringify({ref:'main'})
  });
  // An accepted dispatch is not proof that a refresh or deployment succeeded.
  if(![200,204].includes(dispatched.status)) throw new Error('Unexpected dispatch response');
  return {...status, state:'dispatch_accepted'};
}
export default {
  async scheduled(_event, env) {
    // Evaluate actual execution time: a delayed event must catch up to now.
    const result = await run(env);
    console.log(JSON.stringify({checkedAt:new Date().toISOString(), ...result}));
  },
  async fetch(req, env) {
    if(req.method !== 'GET' || new URL(req.url).pathname !== '/health')
      return new Response('Not found', {status:404});
    const headers = {'Cache-Control':'no-store'};
    if(env.ENABLED !== 'true' || !env.GITHUB_TOKEN)
      return Response.json({state:'not_configured'}, {status:503, headers});
    try {
      const result = await freshness(new Date());
      return Response.json(result, {status:result.state === 'overdue' ? 503 : 200, headers});
    } catch {
      return Response.json({state:'freshness_unavailable'}, {status:503, headers});
    }
  }
};
