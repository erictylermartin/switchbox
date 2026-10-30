from harness import run, SHOTS
results = []
def check(name, ok, detail=''): results.append((name, ok, detail))
G = '({turn:game.turn, left:[...game.passesLeft], passed:[...game.passed], anim:!!anim, over:game.over, ov:!document.getElementById("overlay").hidden, settling:game.settling, round:game.round, totals:[...game.totals], rs:[...game.rs]})'

def settle(pg): pg.wait_for_function('!anim && !game.settling', timeout=8000)

def t_passes(pg):
    pg.evaluate('TICK_MS = 2; Engine.ROUNDS[0].goal = 999; Engine.ROUNDS[1].goal = 999')
    pg.keyboard.press('-'); settle(pg)
    s = pg.evaluate(G); check('pass hands over the turn and uses one pass', s['turn'] == 1 and s['left'] == [2, 3], s)
    check('Pass button is disabled right after the other player passed', pg.is_disabled('#btnPass'))
    pg.keyboard.press('-'); s2 = pg.evaluate(G)
    check('the other player must play after a pass', s2['turn'] == 1 and s2['left'] == [2, 3], s2)
    pg.keyboard.press('3'); settle(pg)
    pg.keyboard.press('-'); s3 = pg.evaluate(G)
    check('no passing twice in a row', s3['turn'] == 0 and s3['left'] == [2, 3], s3)
    # use up player 1's remaining passes
    for _ in range(2):
        pg.keyboard.press('4'); settle(pg)   # P1 drop
        pg.keyboard.press('5'); settle(pg)   # P2 drop
        pg.keyboard.press('-'); settle(pg)   # P1 pass
        pg.keyboard.press('6'); settle(pg)   # P2 drop
    s4 = pg.evaluate(G)
    pg.keyboard.press('2'); settle(pg); pg.keyboard.press('7'); settle(pg)
    pg.keyboard.press('-'); s5 = pg.evaluate(G)
    check('after three passes, no more in this half', s4['left'][0] == 0 and s5['turn'] == 0, (s4, s5))
    check('passes-left counter shows 0', pg.inner_text('#passn0') == '0')
    # second half resets passes
    pg.evaluate('game.round = 1; game.lastChanceFor = 0; game.turn = 0; updateUI()')
    pg.keyboard.press('1'); pg.wait_for_function('!document.getElementById("overlay").hidden', timeout=8000)
    pg.click('#ovBtn'); pg.wait_for_timeout(50)
    s6 = pg.evaluate(G)
    check('passes reset to 3 each for rounds 3-4', s6['round'] == 2 and s6['left'] == [3, 3], s6)

def t_options(pg):
    pg.click('#optionsPanel summary')
    pg.fill('#og0', '7'); pg.fill('#ov0_0', '-3'); pg.fill('#ov3_7', '99')
    pg.click('#optApply'); pg.wait_for_timeout(50)
    r = pg.evaluate('({g: Engine.ROUNDS[0].goal, c7: Engine.ROUNDS[0].vals[7], c8: Engine.ROUNDS[0].vals[8], e0: Engine.ROUNDS[3].vals[0], e15: Engine.ROUNDS[3].vals[15], goalShown: document.getElementById("goal").textContent})')
    check('custom goal and mirrored exit values apply', r == {'g': 7, 'c7': -3, 'c8': -3, 'e0': 99, 'e15': 99, 'goalShown': '7'}, r)
    pg.fill('#ov1_2', '150'); pg.click('#optApply'); pg.wait_for_timeout(30)
    msg = pg.inner_text('#optMsg')
    check('out-of-range values are refused with a clear message', 'from -99 to 99' in msg and pg.evaluate('Engine.ROUNDS[1].vals[10]') != 150, msg)
    pg.reload(); pg.wait_for_timeout(300)
    r2 = pg.evaluate('({g: Engine.ROUNDS[0].goal, v: document.getElementById("og0").value})')
    check('options are remembered after reloading', r2 == {'g': 7, 'v': '7'}, r2)
    pg.click('#optionsPanel summary'); pg.click('#presetOrig'); pg.click('#presetDouble'); pg.click('#optApply'); pg.wait_for_timeout(30)
    r3 = pg.evaluate('Engine.ROUNDS.map(r => r.goal)')
    check('Original values + Double goals presets work', r3 == [20, 80, 40, 160], r3)
    # negative exit values draw and score without errors
    pg.evaluate('TICK_MS = 2; Engine.ROUNDS[0].vals = Engine.ROUNDS[0].vals.map(() => -12); Engine.ROUNDS[0].goal = 999')
    for k in '1234567812345678': pg.keyboard.press(k); settle(pg)
    check('negative exits subtract points', pg.evaluate('game.rs[0] + game.rs[1]') <= 0, pg.evaluate('game.rs'))

def t_lowball(pg):
    pg.click('#optionsPanel summary'); pg.check('#optLow'); pg.click('#optApply')
    pg.select_option('#opp', 'hard'); pg.wait_for_timeout(30)
    check('lowball shows on the round bar', 'LOWBALL' in pg.inner_text('#rname'), pg.inner_text('#rname'))
    pg.evaluate('TICK_MS = 1; AI_DELAY_MS = 10')
    for _ in range(40000):
        s = pg.evaluate(G)
        if s['over']: break
        if s['ov']: pg.click('#ovBtn'); pg.wait_for_timeout(10); continue
        if s['turn'] == 0 and not s['anim'] and not s['settling']: pg.keyboard.press('+')
        pg.wait_for_timeout(10)
    s = pg.evaluate(G); v = pg.inner_text('#ovVerdict')
    a, b = s['totals']
    expected = 'Player 1' if a < b else 'Computer'
    check('a lowball game against Hard finishes', s['over'], s)
    check('lowball: the lower total wins', a == b and 'tie' in v or expected in v, (s['totals'], v))

def t_turn_cap(pg):
    pg.evaluate('TICK_MS = 2; Engine.ROUNDS[0].goal = 999; game.turnsInRound = 119')
    pg.keyboard.press('3'); pg.wait_for_function('!document.getElementById("overlay").hidden', timeout=8000)
    check('a round ends at the turn limit', 'Turn limit' in pg.evaluate('game.log') or pg.evaluate('!document.getElementById("overlay").hidden'))

def t_sound(pg):
    pg.evaluate('TICK_MS = 20; Engine.ROUNDS[0].goal = 999')
    for k in '1357246812': pg.keyboard.press(k); settle(pg)
    pg.click('#btnSound')
    check('sound button turns sound off', pg.get_attribute('#btnSound', 'aria-pressed') == 'false' and pg.inner_text('#btnSound') == 'Sound off')
    pg.reload(); pg.wait_for_timeout(300)
    check('sound setting is remembered', pg.inner_text('#btnSound') == 'Sound off')

def t_mobile_options(pg):
    pg.click('#optionsPanel summary'); pg.wait_for_timeout(50)
    w = pg.evaluate('({sw: document.documentElement.scrollWidth, iw: innerWidth})')
    check('options panel causes no sideways scroll on a phone', w['sw'] <= w['iw'], w)

for t, w in [(t_passes, 900), (t_options, 900), (t_lowball, 900), (t_turn_cap, 900), (t_sound, 900), (t_mobile_options, 390)]:
    errs, _ = run(t, w)
    errs = [e for e in errs if 'ERR_FAILED' not in e]
    check(f'{t.__name__}: no page errors', not errs, errs[:3])
for name, ok, d in results:
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -> {d}'))
print(sum(1 for r in results if r[1]), '/', len(results), 'passed')
