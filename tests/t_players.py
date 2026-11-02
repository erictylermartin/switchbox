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

def swatch(p, hexv): return f'#pal{p} button[data-hex="{hexv}"]'
BOX = 'p => getComputedStyle(document.querySelector(`#pl${p} .box`)).borderColor'

def t_colors(pg):
    check('default colors are cyan and pink', pg.evaluate('COL.p') == ['#5fd3e6', '#f2709c'], pg.evaluate('COL.p'))
    check('the palette starts closed', not pg.is_visible('#pal0'))
    pg.click('#chip0')
    check('the chip opens the palette', pg.is_visible('#pal0') and pg.get_attribute('#chip0', 'aria-expanded') == 'true')
    check('the palette has 8 swatches', pg.locator('#pal0 button').count() == 8)
    check('the current color is marked', pg.get_attribute(swatch(0, '#5fd3e6'), 'aria-checked') == 'true')
    check("the other player's color is disabled", pg.is_disabled(swatch(0, '#f2709c')))
    pg.click(swatch(0, '#ffd75e'))
    check('picking a color closes the palette', not pg.is_visible('#pal0'))
    check('picking a color changes the falling-ball color', pg.evaluate('COL.p[0]') == '#ffd75e')
    check('it changes the CSS variable', pg.evaluate('getComputedStyle(document.documentElement).getPropertyValue("--p1").trim()') == '#ffd75e')
    check('the active box border uses the new color', pg.evaluate(BOX, 0) == 'rgb(255, 215, 94)', pg.evaluate(BOX, 0))
    check('the name uses the new color', pg.evaluate('getComputedStyle(document.getElementById("name0")).color') == 'rgb(255, 215, 94)')
    pg.click('#chip1')
    check("Player 2 can't pick Player 1's new color", pg.is_disabled(swatch(1, '#ffd75e')) and not pg.is_disabled(swatch(1, '#5fd3e6')))
    pg.keyboard.press('Escape')
    check('Escape closes the palette and returns focus to the chip', not pg.is_visible('#pal1') and pg.evaluate('document.activeElement.id') == 'chip1')
    pg.click('#chip1'); pg.keyboard.press('ArrowRight'); pg.keyboard.press('Enter')
    check('arrow keys and Enter pick a color', pg.evaluate('COL.p[1]') not in ('#f2709c', '#ffd75e'), pg.evaluate('COL.p'))
    pg.click('#chip1'); pg.mouse.click(5, 990)
    check('clicking elsewhere closes the palette', not pg.is_visible('#pal1'))
    pg.keyboard.press('3'); pg.wait_for_function('!anim')
    check('Player 2 box uses its color on its turn', pg.evaluate(BOX, 1) != 'rgb(74, 63, 151)', pg.evaluate(BOX, 1))
    saved = pg.evaluate('COL.p.slice()')
    pg.reload(); pg.wait_for_timeout(300)
    check('colors persist after reload', pg.evaluate('COL.p') == saved, (saved, pg.evaluate('COL.p')))

def t_color_clash(pg):
    pg.evaluate('localStorage.setItem("switchbox-settings", JSON.stringify({colors: ["#9be564", "#9be564"]}))')
    pg.reload(); pg.wait_for_timeout(300)
    c = pg.evaluate('COL.p')
    check('a saved clash resets Player 2 to the first free color', c == ['#9be564', '#5fd3e6'], c)

def t_mobile_colors(pg):
    pg.click('#chip1')
    w = pg.evaluate('({sw: document.documentElement.scrollWidth, iw: innerWidth})')
    check('the open palette fits on a phone', w['sw'] <= w['iw'], w)
    pg.screenshot(path=str(SHOTS / 'colors_phone.png'))

for t, w in [(t_names, 900), (t_computer_name, 900), (t_escape, 900), (t_mobile, 390),
             (t_colors, 900), (t_color_clash, 900), (t_mobile_colors, 390)]:
    errs, _ = run(t, w)
    errs = [e for e in errs if 'ERR_FAILED' not in e]
    check(f'{t.__name__}: no page errors', not errs, errs[:3])
for name, ok, d in results:
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -> {d}'))
print(sum(1 for r in results if r[1]), '/', len(results), 'passed')
