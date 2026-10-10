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
    w.eval(`CUR=${JSON.stringify(ticker)};renderAll();`);
    for(const per of ['D','W','M','Y']){
      d.querySelector(`#gPeriod button[data-p="${per}"]`).click();
      const v=w.__gView, res=d.getElementById('gRes');
      assert.ok(!/proven edge|trade this|REAL EDGE/i.test(d.body.textContent),'labels must not claim an edge or instruct trading');
      if(!v.rec){ assert.match(res.textContent,/No forecast|unavailable/); continue; }
      for(const side of ['high','low']){
        const shown=Number(res.querySelector(`[data-side="${side}"]`).dataset.price);
        assert.equal(shown,v[side].price,`${ticker} ${per} ${side}: result must equal the plotted point`);
        assert.ok(v.fc.includes(v[side]),`${ticker} ${per} ${side}: result must be one of the plotted forecast points`);
      }
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
  const before=w.eval('JSON.stringify(DATA_ALL)');
  response='const DATA_ALL = {"TSLA":{"price":1}};';
  await d.getElementById('gUpd').onclick();
  assert.equal(w.eval('JSON.stringify(DATA_ALL)'),before,'invalid payload must not replace data');
  assert.equal(d.getElementById('gUpd').className,'bad');
  failNetwork=true;
  await d.getElementById('gUpd').onclick();
  assert.equal(w.eval('JSON.stringify(DATA_ALL)'),before);
  failNetwork=false;response=payload;
  await d.getElementById('gUpd').onclick();
  assert.notEqual(d.getElementById('gUpd').className,'bad');
  assert.equal(d.getElementById('gUpd').disabled,false);
  assert.deepEqual(errors,[]);
  console.log('PASS: all tickers and periods render with results equal to plotted points; hover/touch and keyboard inspect; invalid/offline updates preserve data; recovery succeeds.');
  process.exit(0);
})().catch(e=>{console.error(e);process.exit(1);});
