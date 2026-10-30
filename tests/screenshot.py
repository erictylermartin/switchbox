from harness import run, SHOTS
SP=str(SHOTS) + '/'
def fn(pg):
    pg.evaluate('TICK_MS = 5; Engine.ROUNDS[0].goal = 999')
    for k in [1,3,5,7,2,4,6,0,3,5,1,6]:
        pg.keyboard.press(str(k+1)); pg.wait_for_timeout(120)
    pg.select_option('#opp', 'hard'); pg.wait_for_timeout(50)
    pg.evaluate('TICK_MS = 300; AI_DELAY_MS = 60')
    pg.keyboard.press('3'); pg.wait_for_timeout(1400)
    pg.screenshot(path=SP+'v4_desk.png')
    pg.locator('canvas').screenshot(path=SP+'v4_canvas.png', scale='device')
errs,_=run(fn, 1100); print(errs)
