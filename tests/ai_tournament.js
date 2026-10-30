// Plays full 4-round games between AI levels using the page's own engine.
const fs = require('fs');
const h = fs.readFileSync(require('path').join(__dirname, '..', 'index.html'), 'utf8');
const Engine = new Function(h.split('<script id="engine">')[1].split('</script>')[0] + ';return Engine;')();
function mulberry(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function game(lv, seed) {
  const rng = mulberry(seed);
  let board = Engine.newBoard(rng), totals = [0,0], turn = seed % 2, moves = 0, passed = [false,false];
  for (const R of Engine.ROUNDS) {
    let st = { board, rs: [0,0], turn, lc: null, done: false };
    let guard = 0;
    while (!st.done && guard++ < 400) {
      const c = Engine.chooseMove(st, lv[st.turn], R.vals, R.goal, rng, !passed[st.turn]);
      passed[st.turn] = c < 0;
      st = Engine.applyMove(st, c, R.vals, R.goal); moves++;
    }
    if (!st.done) return null;              // stalled round
    const s = Engine.settle(st.rs, R.goal);
    totals[0] += s[0].total; totals[1] += s[1].total;
    board = st.board; turn = st.turn;
  }
  return { totals, moves };
}
const N = +process.argv[2] || 40;
for (const [a, b] of [['medium','easy'], ['hard','easy'], ['hard','medium']]) {
  let wa = 0, wb = 0, ties = 0, stalls = 0, margin = 0, t0 = Date.now(), moves = 0;
  for (let i = 0; i < N; i++) {
    // alternate seats so neither side always goes first
    const flip = i % 2, lv = flip ? [b, a] : [a, b];
    const r = game(lv, 1000 + i);
    if (!r) { stalls++; continue; }
    moves += r.moves;
    const A = r.totals[flip ? 1 : 0], B = r.totals[flip ? 0 : 1];
    if (A > B) wa++; else if (B > A) wb++; else ties++;
    margin += A - B;
  }
  const ms = (Date.now() - t0) / moves;
  console.log(`${a.padEnd(6)} vs ${b.padEnd(6)}: ${a} wins ${wa}, ${b} wins ${wb}, ties ${ties}, stalls ${stalls}, avg margin ${(margin / (N - stalls)).toFixed(1)}, ~${ms.toFixed(1)} ms/move`);
}
