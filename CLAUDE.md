# Switchbox

A browser recreation of **Switchbox**, the two-player strategy game by Todd Heimarck
from COMPUTE! magazine, March 1986 (issue 70, page 34). Players drop balls into a
pyramid of two-way switches and chain reactions score points.

The game ships as **one self-contained `index.html`**, published as a Claude artifact
(a private, shareable link). Keep it that way unless the owner decides otherwise.

## Working agreement (read first)

1. **Propose before building.** For any feature or non-trivial change, describe what
   you plan to change and why, list open questions with a recommended answer, and
   wait for approval. Small bug fixes the owner asked for can go straight ahead.
2. **Use the cheapest model that can do the job.** Routine work (running tests,
   screenshots, mechanical edits, searching the code) can go to a faster/cheaper
   model or subagent. Keep design decisions and tricky logic on the main model.
3. **Test before publishing.** Run both browser suites and fix failures first.
   Look at one screenshot for any visual change.
4. **One look, not a loop.** After a visual change, take one screenshot, make one
   round of fixes, then show the owner. The owner reviews; don't polish endlessly.
5. **Never change the switch art or game rules on your own.** Both were settled with
   the owner (see "Decisions" below). Ask first.

## Layout

```
index.html                 the whole game: markup, CSS, engine, renderer, UI
tests/harness.py           Playwright harness (wraps index.html like the artifact host)
tests/t_suite.py           33 core checks: play, input, full games, phone layout, computer opponent
tests/t_options.py         25 checks: passes, lowball, custom values, turn limit, sound
tests/t_players.py         49 checks: player names and colors (later: voice)
tests/ai_tournament.js     AI-vs-AI games in Node to measure difficulty levels
tests/screenshot.py        renders a mid-game board to tests/screenshots/
tools/switch-sketchpad.html  pixel editor the owner used to draw the switch
docs/next-features.md      approved spec for the next batch of work
```

Inside `index.html`, in order:
- `<style>`: tokens on `:root` (cabinet colors plus the playfield colors `--field`,
  `--wall`, `--lane`, `--sw`, `--ball`, `--p1`, `--p2`). Single dark look by design.
- `<script id="engine">`: **pure game logic, no DOM.** `Engine.simulate(board, col)`,
  `Engine.ROUNDS`, `Engine.score`, `Engine.settle`, and the AI (`applyMove`, `evaluate`,
  `negamax`, `chooseMove`). Tests load this block straight into Node. Keep it DOM-free.
- Main `<script>`: rendering (canvas), sound, settings, turn flow, computer opponent,
  options panel, input, boot.

## Commands

```bash
pip install playwright && python -m playwright install chromium   # once
python tests/t_suite.py        # expect 33 / 33
python tests/t_options.py      # expect 25 / 25
python tests/t_players.py      # expect 49 / 49
node tests/ai_tournament.js 40 # difficulty check (Hard ~even with Medium, both crush Easy)
python tests/screenshot.py     # writes tests/screenshots/*.png
```

## Publishing

Publish `index.html` with the Artifact tool to the existing artifact:
https://claude.ai/artifact/SGyf1ia8WCPUEoSTjHj3Fs (read it first, then publish to that `url`).
Artifact rules that matter here:
- Scripts may load only from cdnjs.cloudflare.com, cdn.jsdelivr.net/npm, unpkg.com,
  pinned to an exact version at least two weeks old. Fonts only from Google Fonts.
- No fetch/XHR/WebSocket to other hosts. localStorage works but is per-viewer;
  wrap every read and write in try/catch.
- Sound may start only after a user gesture.

## Decisions already made with the owner

- **Board:** 5 levels (4, 5, 6, 7, 8 switches), 8 entries, 16 exits; switches start in
  random directions; the board carries over between rounds.
- **Switch art:** drawn pixel for pixel by the owner in the sketchpad (`SWITCH_ART`).
  A slanted slab with a level top, ball resting on it, bottom two rows extend as the
  flat trigger bar across the pivot. Leaning right is the mirror image. The ball was
  widened from 10 to 11 px (with the owner's approval) so it centres in the 15-px
  channel on both sides of a pivot.
- **Rounds:** Equality (all 2, goal 10), Fibonacci (goal 40), Counting 1-8 (goal 20),
  Squares 1-64 (goal 80; read off a round-4 screenshot of the original).
- **Round end:** when a player reaches the goal, the other gets one last turn. Settlement:
  goal added as bonus to anyone at or over it; the point difference is added to the
  higher scorer and taken from the lower. 120-turn cap per round (guards custom
  negative values).
- **Pass limit (default on):** 3 passes per half (rounds 1-2, 3-4), no passing twice
  in a row, after one player passes the other must play.
- **Lowball:** same settlement, lowest total wins; AI negates its evaluation.
- **Computer opponent:** always Player 2. Easy = random (the 1986 solitaire rules).
  Medium = best immediate move. Hard = 3-ply negamax, takes its second-best move 30%
  of the time (owner wanted Hard "doable").
- **Player names:** renamed by clicking the name in a score box (hover underlines it);
  no name inputs or note in the Options panel (owner's call, overriding the spec). Apply
  as typed, shown in capitals, blank falls back to PLAYER 1 / PLAYER 2 / COMPUTER.
  Stored as `names: [p1, p2Human, p2Computer]`. The computer's box shows
  `NAME · LEVEL`; only the name part is editable. `nameOf(p)` is the single source.
- **Player colors:** a small chip next to each name opens a 4 x 2 palette (`PALETTE`,
  8 retro colors from the spec, unchanged after a contrast check). The other player's
  color is disabled; a saved clash resets Player 2 to the first free color. One color
  per side (the computer shares Player 2's). `applyColors()` sets `--p1`/`--p2` on
  `:root` and `COL.p` together. Stored as `colors: ['#…', '#…']`.
- **Options** apply when the owner presses "Apply and start new game"; settings live
  in localStorage key `switchbox-settings`.

## Deferred

- **Faithful / Strict toggle.** Needs the original BASIC listing to copy exact quirks
  (two balls reaching one switch on the same step; ball processing order). The listing
  is in a ZIP the cloud workspace could not download:
  https://www.gamingalexandria.com/typingtaskforce/Commodore%2064/Switchbox%20(Todd%20Heimarck)/Switchbox%20(Todd%20Heimarck).zip
  The owner will attach it later.
- **Online multiplayer (v2).** Not planned for now; the owner wants to keep it local.
