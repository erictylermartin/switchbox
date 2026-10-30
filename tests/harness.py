"""Shared Playwright harness. Wraps index.html in a document skeleton (as the
artifact host does) and runs a test function in headless Chromium."""
import pathlib, tempfile
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
GAME = ROOT / 'index.html'
OUT = pathlib.Path(tempfile.gettempdir()) / 'switchbox-test-page.html'
SHOTS = ROOT / 'tests' / 'screenshots'
SHOTS.mkdir(exist_ok=True)
OUT.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" '
               'content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>'
               + GAME.read_text() + '</body></html>')

def run(fn, width=900):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': width, 'height': 1000})
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        pg.on('console', lambda m: m.type == 'error' and 'fonts.g' not in m.text and errs.append('CONSOLE ' + m.text))
        pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())   # keep tests offline
        pg.goto(OUT.as_uri())
        pg.wait_for_timeout(300)
        res = fn(pg)
        b.close()
        return errs, res
