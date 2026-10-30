from harness import run, SHOTS
results = []
def check(name, ok, detail=''):
    results.append((name, ok, detail))

STATE = '({turn:game.turn, rs:[...game.rs], totals:[...game.totals], round:game.round, over:game.over, anim:!!anim, settling:game.settling, ov:!document.getElementById("overlay").hidden, balls:game.board.flat().filter(s=>s.ball).length, lc:game.lastChanceFor})'

def t_real_speed(pg):
    pg.evaluate('Engine.ROUNDS[0].goal = 999')    # keep the round from ending mid-test
    for i in range(8):
        pg.keyboard.press(str(i+1)); pg.wait_for_timeout(50); pg.wait_for_function('!anim && !game.settling', timeout=5000)
    s = pg.evaluate(STATE)
    check('8 drops at normal speed all finish', not s['anim'], s)
    check('turn alternates', s['turn'] == 0, s)
    pg.screenshot(path=str(SHOTS / 'shot.png'))

def t_columns(pg):
    pg.evaluate('Engine.ROUNDS[0].goal = 999')
    pg.evaluate('TICK_MS = 150')
    bad = []
    for k in range(8):
        pt = pg.evaluate(f'''(() => {{ const r = cv.getBoundingClientRect();
            return {{x: r.left + px(Engine.ENTRY_X[{k}]) * r.width / W, y: r.top + 30 * r.height / H}}; }})()''')
        pg.mouse.click(pt['x'], pt['y'])
        col = pg.evaluate('anim ? anim.col : null')
        if col != k: bad.append((k, col))
        pg.wait_for_timeout(1100)
    check('tapping each of the 8 columns drops in that column', not bad, bad)

def t_full_game(pg):
    pg.evaluate('TICK_MS = 1')
    drops = 0; prev = pg.evaluate(STATE); anomalies = []; rounds_seen = set(); lastchance_seen = False
    for step in range(20000):
        s = pg.evaluate(STATE)
        rounds_seen.add(s['round'])
        if s['lc'] is not None: lastchance_seen = True
        if s['balls'] > 30 or s['balls'] < 0: anomalies.append(('balls', s))
        if s['over']: break
        if s['ov']:
            pg.click('#ovBtn'); pg.wait_for_timeout(30); continue
        if s['anim'] or s['settling']:
            pg.wait_for_timeout(20); continue
        pg.keyboard.press('+'); drops += 1
        pg.wait_for_timeout(25)
    s = pg.evaluate(STATE)
    check('a full 4-round game plays to the end', s['over'] and rounds_seen == {0,1,2,3}, {'drops': drops, 'rounds': sorted(rounds_seen), 'final': s})
    check('last-chance turn triggered', lastchance_seen)
    check('final overlay shows a winner', pg.evaluate('document.getElementById("ovVerdict").textContent'), pg.evaluate('document.getElementById("ovVerdict").textContent'))
    pg.click('#ovBtn'); pg.wait_for_timeout(50)
    s = pg.evaluate(STATE)
    check('Play again resets the game', not s['over'] and s['round'] == 0 and s['totals'] == [0,0] and s['balls'] == 0, s)
    check('no ball-count anomalies', not anomalies, anomalies[:3])

def t_settling_blocks_input(pg):
    pg.evaluate('TICK_MS = 5')
    pg.evaluate('game.lastChanceFor = 0; game.turn = 0; updateUI()')
    pg.keyboard.press('4'); pg.wait_for_timeout(150)
    s1 = pg.evaluate(STATE)
    pg.keyboard.press('5'); pg.wait_for_timeout(30)
    s2 = pg.evaluate(STATE)
    pg.wait_for_timeout(900)
    s3 = pg.evaluate(STATE)
    check('input is blocked while a round wraps up', s1['settling'] and not s2['anim'], (s1, s2))
    check('round-end summary appears after last chance', s3['ov'], s3)
    pg.keyboard.press('3'); pg.wait_for_timeout(50)
    check('keys do nothing behind the summary', not pg.evaluate('!!anim'))
    pg.click('#ovBtn'); pg.wait_for_timeout(50)
    s4 = pg.evaluate(STATE)
    check('next round starts with scores reset and board kept', s4['round'] == 1 and s4['rs'] == [0,0] and s4['balls'] == s3['balls'], (s3, s4))

def t_pass_and_mash(pg):
    pg.keyboard.press('-'); pg.wait_for_timeout(50)
    check('pass hands the turn over', pg.evaluate('game.turn') == 1)
    for i in range(200):
        pg.keyboard.press(str(i % 8 + 1))
    pg.wait_for_timeout(1500)
    for i in range(20):
        pg.click('#btnRandom', force=True)
    pg.wait_for_timeout(1500)
    check('key mashing leaves the game responsive', not pg.evaluate('!!anim'))

def t_mobile(pg):
    pg.evaluate('Engine.ROUNDS[0].goal = 999')
    w = pg.evaluate('({sw: document.documentElement.scrollWidth, iw: innerWidth})')
    check('no sideways scroll at phone width', w['sw'] <= w['iw'], w)
    box = pg.locator('canvas').bounding_box()
    pg.mouse.click(box['x'] + box['width'] * 0.47, box['y'] + 20); pg.wait_for_timeout(50); pg.wait_for_function('!anim', timeout=5000)
    check('tap works at phone width', pg.evaluate('game.turn') == 1 and not pg.evaluate('!!anim'))
    pg.screenshot(path=str(SHOTS / 'shot_mobile.png'), full_page=True)

allerrs = []
for t, w in [(t_real_speed, 900), (t_columns, 900), (t_full_game, 900), (t_settling_blocks_input, 900), (t_pass_and_mash, 900), (t_mobile, 390)]:
    errs, _ = run(t, w)
    errs = [e for e in errs if 'ERR_FAILED' not in e]
    check(f'{t.__name__}: no page errors', not errs, errs[:3])
for name, ok, d in results:
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -> {d}'))
print(sum(1 for r in results if r[1]), '/', len(results), 'passed')

# ---------------- computer opponent ----------------
results2 = []
def t_vs_computer(pg):
    pg.select_option('#opp', 'hard'); pg.wait_for_timeout(50)
    pg.evaluate('TICK_MS = 1; AI_DELAY_MS = 30; window.__drops = []; const o = startDrop; startDrop = function (c) { __drops.push(game.turn); o(c); }; 0')
    blocked_ok = True; tries = 0
    for step in range(40000):
        s = pg.evaluate(STATE)
        if s['over']: break
        if s['ov']: pg.click('#ovBtn'); pg.wait_for_timeout(20); continue
        if False:
            before = pg.evaluate('__drops.length')
            pg.keyboard.press('5')                           # a person tries to move for the computer
            after = pg.evaluate('__drops.slice(' + str(before) + ')')
            if any(t == 0 for t in after): blocked_ok = False
            tries += 1
        if s['turn'] == 0 and not s['anim'] and not s['settling']:
            pg.keyboard.press('+')
        pg.wait_for_timeout(15)
    s = pg.evaluate(STATE); drops = pg.evaluate('__drops')
    check('a full game against the computer reaches the end', s['over'], s)
    check('the computer takes its own turns', drops.count(1) > 10, {'cpu_drops': drops.count(1), 'human_drops': drops.count(0)})
    check('Player 2 panel shows the computer', 'COMPUTER' in pg.inner_text('#name1'))
    v = pg.inner_text('#ovVerdict'); check('final verdict names a winner', 'wins' in v or 'tie' in v, v)

def t_switch_modes(pg):
    pg.evaluate('TICK_MS = 5; AI_DELAY_MS = 30')
    pg.keyboard.press('2'); pg.wait_for_function('!anim')           # P1 moves, now P2 (human) to move
    pg.select_option('#opp', 'medium'); pg.wait_for_timeout(400)     # switching hands P2 to the computer
    check('switching to the computer mid-game lets it take the waiting turn', pg.evaluate('game.turn') == 0 and not pg.evaluate('!!anim'))
    pg.select_option('#opp', 'human'); pg.wait_for_timeout(30)
    check('switching back to two players restores Player 2', pg.inner_text('#name1') == 'PLAYER 2')

def t_block(pg):
    pg.select_option('#opp', 'hard')
    pg.evaluate('TICK_MS = 5; AI_DELAY_MS = 800; window.__drops = []; const o = startDrop; startDrop = function (c) { __drops.push(game.turn); o(c); }; 0')
    pg.keyboard.press('1'); pg.wait_for_function('!anim && game.turn === 1')
    for k in '2345': pg.keyboard.press(k)
    box = pg.locator('canvas').bounding_box(); pg.mouse.click(box['x'] + box['width'] * 0.47, box['y'] + 20)
    pg.click('#btnRandom', force=True); pg.click('#btnPass', force=True)
    pg.wait_for_timeout(150)
    mid = pg.evaluate('({d: __drops.slice(), turn: game.turn})')
    pg.wait_for_function('__drops.length >= 2', timeout=5000)
    end = pg.evaluate('__drops.slice()')
    check("keys, taps and buttons do nothing during the computer's turn", mid == {'d': [0], 'turn': 1}, mid)
    check('the computer then moves on its own', end[:2] == [0, 1], end)

for t, w in [(t_vs_computer, 900), (t_switch_modes, 900), (t_block, 900)]:
    errs, _ = run(t, w)
    errs = [e for e in errs if 'ERR_FAILED' not in e]
    check(f'{t.__name__}: no page errors', not errs, errs[:3])
for name, ok, d in results[-11:]:
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -> {d}'))
print(sum(1 for r in results if r[1]), '/', len(results), 'passed overall')
