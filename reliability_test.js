const assert=require('node:assert/strict');
require('node:child_process').execFileSync(process.execPath, ['pin_test.js'], {stdio:'inherit'});
const fs=require('node:fs');
const {JSDOM}=require('jsdom');
const html=fs.readFileSync('index.html','utf8');
const payload=fs.readFileSync('data.js','utf8');
let response=payload, failNetwork=false;
const errors=[];
const ctx=new Proxy({}, {get:(o,k)=>k==='measureText'?()=>({width:10}):()=>{},set:()=>true});
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://elljp1.github.io/stock-dashboard/',beforeParse(w){
  w.HTMLCanvasElement.prototype.getContext=()=>ctx;
  w.fetch=async()=>{if(failNetwork)throw Error('offline');return {ok:true,status:200,text:async()=>response};};
  w.addEventListener('error',e=>errors.push(e.message));
}});
const w=dom.window,d=w.document;
const delay=()=>new Promise(r=>setTimeout(r,30));
(async()=>{
  await delay();
  for(const ticker of w.eval('Object.keys(DATA_ALL)')){
    w.eval(`CUR=${JSON.stringify(ticker)};renderAll(DATA_ALL[CUR]);`);
    const forecasts=w.eval('DATA_ALL[CUR].predictions');
    const chartRow=d.querySelector('[data-chart-targets]');
    for(const side of ['high','low']){
      const p=forecasts.filter(p=>p.type===side).sort((a,b)=>side==='high'?b.price-a.price:a.price-b.price)[0];
      const cell=chartRow.children[side==='high'?1:2];
      assert.ok(cell.textContent.includes(p.isoDate),'table date must match chart target for '+ticker);
      assert.equal(Number(cell.querySelector('.big').textContent.replace(/[$,]/g,'')),p.price,'table price must match chart for '+ticker);
    }
    for(const cell of d.querySelectorAll('[data-forecast-kind="range"]')){
      assert.ok(cell.textContent.includes('RANGE ESTIMATE'));
      assert.ok(cell.textContent.includes('not a turn date'));
      assert.ok(!cell.textContent.includes(' hour '),'range must not claim a turning time');
    }
    const c=d.getElementById('chart');
    c.getBoundingClientRect=()=>({left:0,top:0,width:c.__w,height:c.__h});
    assert.equal(typeof c.onpointermove,'function');
    c.onpointermove({clientX:c.__w/2,clientY:c.__h/2});
    assert.match(d.getElementById('chartTooltip').textContent,/\d{4}-\d{2}-\d{2}/);
    assert.match(d.getElementById('chartTooltip').textContent,/\$/);
    c.onpointerleave();
    assert.equal(d.getElementById('chartTooltip').style.display,'none');
    c.onkeydown({key:'ArrowLeft',preventDefault(){}});
    assert.match(d.getElementById('chartTooltip').textContent,/Actual daily close/);
  }
  assert.match(d.getElementById('updated').textContent,/price as of|exact quote time unavailable/);
  const before=w.eval('JSON.stringify(DATA_ALL)');
  response='const DATA_ALL = {"TSLA":{"price":1}};';
  await d.getElementById('btnUpdate').onclick();
  assert.equal(w.eval('JSON.stringify(DATA_ALL)'),before,'invalid payload must not replace data');
  assert.equal(d.getElementById('btnUpdate').disabled,false);
  failNetwork=true;
  await d.getElementById('btnUpdate').onclick();
  assert.equal(w.eval('JSON.stringify(DATA_ALL)'),before);
  failNetwork=false;response=payload;
  await d.getElementById('btnUpdate').onclick();
  assert.match(d.getElementById('updStatus').textContent,/Analysis generated/);
  assert.equal(d.getElementById('btnUpdate').disabled,false);
  assert.deepEqual(errors,[]);
  console.log('PASS: all tickers render; hover/touch handler and keyboard inspect; invalid/offline updates preserve data; recovery succeeds.');
  dom.window.close();
})().catch(e=>{console.error(e);dom.window.close();process.exitCode=1;});
