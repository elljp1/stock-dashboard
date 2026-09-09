const assert = require('node:assert/strict');
const fs = require('node:fs');
const {createHash, webcrypto} = require('node:crypto');
const {JSDOM} = require('jsdom');
// Test with a fixture PIN only; never recover or enter the production PIN.
const fixture = '680135';
const hash = createHash('sha256').update('stk-dash-2026|' + fixture).digest('hex');
const template = fs.readFileSync('dashboard.html', 'utf8');
const gate = template.slice(template.indexOf('<div id="pinGate"'),
  template.indexOf('</script>', template.indexOf('<div id="pinGate"')) + 9)
  .replace(/var GATE_H = "[a-f0-9]+";/, 'var GATE_H = "' + hash + '";');
const opened = [];
function page({saved, session, blocked = []} = {}) {
  const dom = new JSDOM(gate, {
    url:'https://pin-test.invalid/', runScripts:'dangerously', pretendToBeVisual:true,
    beforeParse(w) {
      w.TextEncoder = TextEncoder;
      Object.defineProperty(w.crypto, 'subtle', {value:webcrypto.subtle});
      if(saved) w.localStorage.setItem('pinOk', saved);
      if(session) w.sessionStorage.setItem('pinOk', session);
      for(const name of blocked) Object.defineProperty(w, name, {get(){throw Error('blocked');}});
    }
  });
  opened.push(dom);
  return dom.window;
}
const tick = () => new Promise(r => setTimeout(r, 25));
async function unlocked(w) {
  const deadline = Date.now() + 3000;
  while(w.document.getElementById('pinGate') && Date.now() < deadline) await tick();
}
function input(w, value) {
  const field = w.document.getElementById('pinIn');
  field.value = value;
  field.dispatchEvent(new w.Event('input', {bubbles:true}));
}
(async () => {
  const w = page();
  await tick();
  assert.equal(w.document.activeElement.id, 'pinIn', 'PIN must focus on arrival');
  input(w, fixture.slice(0, -1));
  await tick();
  assert.ok(w.document.getElementById('pinGate'), 'partial PIN remains locked');
  assert.equal(w.document.getElementById('pinMsg').textContent, '');
  input(w, fixture);
  await unlocked(w);
  assert.equal(w.document.getElementById('pinGate'), null, 'correct PIN unlocks without button');
  const saved = w.localStorage.getItem('pinOk');
  assert.ok(saved);
  assert.equal(page({saved}).document.getElementById('pinGate'), null, 'reload restores unlock before dashboard helper');
  assert.equal(page({session:w.sessionStorage.getItem('pinOk'), blocked:['localStorage']}).document.getElementById('pinGate'), null);
  for(const value of ['broken json', JSON.stringify({h:hash,t:Date.now()-31*864e5}), JSON.stringify({h:hash,t:Date.now()+864e5}), JSON.stringify({h:'wrong',t:Date.now()})])
    assert.ok(page({saved:value}).document.getElementById('pinGate'), 'invalid/expired unlock stays locked');
  const retry = page();
  input(retry, '000000');
  retry.document.getElementById('pinGo').click();
  input(retry, fixture);
  await unlocked(retry);
  assert.equal(retry.document.getElementById('pinGate'), null, 'stale failure cannot erase correct input');
  const noStore = page({blocked:['localStorage','sessionStorage']});
  input(noStore, fixture);
  await unlocked(noStore);
  assert.equal(noStore.document.getElementById('pinGate'), null, 'blocked storage must not prevent unlock');
  const typed = page();
  typed.document.getElementById('pinIn').blur();
  for(const key of fixture) typed.document.dispatchEvent(new typed.KeyboardEvent('keydown', {key,bubbles:true}));
  await unlocked(typed);
  assert.equal(typed.document.getElementById('pinGate'), null, 'typing on the page enters PIN without selecting field');
  console.log('PASS: PIN focus, automatic unlock, reload persistence, invalid/expired sessions, input races and blocked storage.');
})().catch(e => {console.error(e);process.exitCode=1;}).finally(() => opened.forEach(d => d.window.close()));
