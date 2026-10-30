from harness import run, SHOTS
results = []
def check(name, ok, detail=''): results.append((name, ok, detail))

def rename(pg, p, text, key='Enter'):
    pg.click(f'#name{p}')
    pg.fill(f'#nameIn{p}', text)
    if key: pg.keyboard.press(key)

def overlay_up(pg): pg.wait_for_function('!document.getElementById("overlay").hidden', timeout=8000)

def t_names(pg):
    pg.evaluate('TICK_MS = 2; Engine.ROUNDS[0].goal = 999')
    check('default names in the boxes', pg.inner_text('#name0') == 'PLAYER 1' and pg.inner_text('#name1') == 'PLAYER 2')
    pg.click('#name0')
    check('clicking the name opens a text field', pg.is_visible('#nameIn0') and not pg.is_visible('#name0'))
    check('the field is limited to 10 characters', pg.get_attribute('#nameIn0', 'maxlength') == '10')
    pg.fill('#nameIn0', 'Jody')
    check('the box label updates while typing, in capitals', pg.inner_text('#name0') == 'JODY')
    check('the status line updates while typing', 'JODY' in pg.inner_text('#status'), pg.inner_text('#status'))
    pg.keyboard.press('Enter')
    check('Enter closes the field', pg.is_visible('#name0') and not pg.is_visible('#nameIn0'))
    check('the name is stored as typed', pg.evaluate('settings.names[0]') == 'Jody')
    rename(pg, 1, 'frank')
    pg.keyboard.press('3'); pg.wait_for_function('!anim && !game.settling', timeout=5000)
    check('the status line uses the new name on later turns', 'FRANK' in pg.inner_text('#status'), pg.inner_text('#status'))
    rename(pg, 1, 'Nobody', key='Escape')
    check('Escape puts the old name back', pg.inner_text('#name1') == 'FRANK' and pg.evaluate('settings.names[1]') == 'frank')
    rename(pg, 1, '   ')
    check('a blank name falls back to the default', pg.inner_text('#name1') == 'PLAYER 2')
    rename(pg, 1, 'Frank')
    B = '[game.turn, game.board.flat().filter(s => s.ball).length, !!anim]'
    before = pg.evaluate(B)
    pg.click('#name0'); pg.keyboard.type('5'); pg.wait_for_timeout(50)
    check('typing a number in the name field does not drop a ball', pg.evaluate(B) == before, (before, pg.evaluate(B)))
    pg.keyboard.press('Enter')
    rename(pg, 0, 'Jody')
    # round table and verdict
    pg.evaluate('game.round = 3; game.lastChanceFor = 0; game.turn = 0; updateUI()')
    pg.keyboard.press('1'); overlay_up(pg)
    heads = pg.locator('#ovTable thead th').all_inner_texts()
    check('round table headers show the names', heads[1:] == ['JODY', 'FRANK'], heads)
    v = pg.inner_text('#ovVerdict')
    check('the final verdict uses a name', 'tie' in v or 'JODY' in v or 'FRANK' in v, v)
    pg.reload(); pg.wait_for_timeout(300)
    check('names persist after reload', pg.inner_text('#name0') == 'JODY' and pg.inner_text('#name1') == 'FRANK')

def t_computer_name(pg):
    rename(pg, 1, 'Frank')
    pg.select_option('#opp', 'medium'); pg.wait_for_timeout(50)
    check('switching to the computer shows its default name', pg.inner_text('#name1') == 'COMPUTER', pg.inner_text('#name1'))
    check('the difficulty shows next to the name', pg.inner_text('#lvl1').strip() == '· MEDIUM', pg.inner_text('#lvl1'))
    pg.wait_for_function('game.turn === 0 && !anim', timeout=5000)
    rename(pg, 1, 'Hal')
    check("the computer's name is editable", pg.inner_text('#name1') == 'HAL')
    check('the human Player 2 name is kept separately', pg.evaluate('settings.names') == ['', 'Frank', 'Hal'], pg.evaluate('settings.names'))
    pg.select_option('#opp', 'human'); pg.wait_for_timeout(50)
    check('switching back shows the human name', pg.inner_text('#name1') == 'FRANK' and pg.inner_text('#lvl1') == '')
    pg.reload(); pg.wait_for_timeout(300)
    pg.select_option('#opp', 'hard'); pg.wait_for_timeout(50)
    check("the computer's stored name persists after reload", pg.inner_text('#name1') == 'HAL')

def t_escape(pg):
    rename(pg, 0, '<b>x</b>')
    st = pg.evaluate('document.querySelector("#status .who1")?.textContent')
    check('names with markup are shown as text', pg.inner_text('#name0') == '<B>X</B>' and st == '<B>X</B>', st)

def t_mobile(pg):
    rename(pg, 0, 'Wwwwwwwwww'); rename(pg, 1, 'Mmmmmmmmmm')
    w = pg.evaluate('({sw: document.documentElement.scrollWidth, iw: innerWidth})')
    check('long names cause no sideways scroll on a phone', w['sw'] <= w['iw'], w)
    pg.click('#name0')
    w = pg.evaluate('({sw: document.documentElement.scrollWidth, iw: innerWidth})')
    check('the open name field fits on a phone', w['sw'] <= w['iw'], w)
    pg.keyboard.press('Enter')
    pg.screenshot(path=str(SHOTS / 'names_phone.png'))

for t, w in [(t_names, 900), (t_computer_name, 900), (t_escape, 900), (t_mobile, 390)]:
    errs, _ = run(t, w)
    errs = [e for e in errs if 'ERR_FAILED' not in e]
    check(f'{t.__name__}: no page errors', not errs, errs[:3])
for name, ok, d in results:
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -> {d}'))
print(sum(1 for r in results if r[1]), '/', len(results), 'passed')
