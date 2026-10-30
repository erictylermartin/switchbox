# Next features: player names, colors, SAM voice

**Status: approved by the owner on 2026-10-30.** Build these three in order, each as its
own commit, running both test suites before each commit. Anything not covered here,
or any part that turns out not to work as written: stop and ask the owner.

---

## 1. Player names

**What:** each player can set a name, shown in the game wherever "Player 1",
"Player 2" or "Computer" appears today.

- New "Players" section at the **top of the Options panel** (`#optionsPanel`).
- One text input per player, `maxlength="10"`. Store as typed; **display in capitals**
  (like the original screens: JODY, FRANK).
- Defaults: `PLAYER 1`, `PLAYER 2`. When the opponent is the computer, Player 2's
  default is `COMPUTER`, and it is editable.
- Empty or whitespace-only input falls back to the default.
- Names **apply immediately** (no new game). This differs from the other options,
  which apply on "Apply and start new game". Say so in a one-line note under the inputs.
- Show the names in: the player boxes (`#name0`/`#name1`, add an id to Player 1's
  label), the status line, the round-end table headers (today "P1"/"CPU"), and the
  final verdict.
- Where to change it: `nameOf(p)` in the turn-flow section is the single source for
  names in messages; `updateUI()` sets the box labels; `endRound()` builds the table.
- Persist in `switchbox-settings` as `names: ['…', '…']`, keeping one stored name for
  a human Player 2 and one for the computer: `names: [p1, p2Human, p2Computer]`.

## 2. Player colors (curated palette)

**What:** each player picks a color from a fixed retro palette.

- Palette (8 swatches; check each is readable on the board field `--field: #8a84dc`
  and as text on the dark cabinet `--crt: #1b1640`, and adjust a value if not):

  | Name | Hex |
  |---|---|
  | Cyan | `#5fd3e6` (P1 default) |
  | Pink | `#f2709c` (P2 default) |
  | Gold | `#ffd75e` |
  | Lime | `#9be564` |
  | Orange | `#ff9f43` |
  | Red | `#ff5c5c` |
  | Cream | `#f4e9cf` |
  | Teal | `#2ec4b6` |

- UI: a row of swatch buttons per player in the Players section (radio-group
  semantics, visible focus, the selected swatch marked by more than color alone, e.g.
  a thick border and a check mark).
- The two players **cannot share a color**: the swatch the other player holds is
  disabled for this player.
- A player's color tints: their falling balls (`COL.p[p]`), their score-box border and
  glow (`.player.active.p1/.p2` in CSS; switch these to a CSS variable set from JS),
  their name label and status-line name (`.who1`/`.who2`), and the entry-bar hover
  highlight in `drawEntries`.
- Apply immediately, persist in `switchbox-settings` as `colors: ['#…', '#…']`.
- Note: `COL` is read from CSS once at load; update `COL.p[0]`/`COL.p[1]` and the CSS
  variables together whenever a color changes.

## 3. Computer voice (SAM)

**What:** at key moments the game speaks in the voice of **SAM (Software Automatic
Mouth)**, the 1982 speech program for the Commodore 64, the way the 1986 Amiga version
spoke player names.

### Phrases (key moments only; never every turn)

| Moment | Phrase |
|---|---|
| New game | "Welcome to Switchbox. {P1} versus {P2}." |
| Chain reaction, 4 or more balls exit in one drop | "{Name} scores {points}." |
| Start of rounds 2, 3, 4 | "Round two. Fibonacci." / "Round three. Counting." / "Round four. Squares." |
| Game over | "{Name} wins." or "Tie game." |

Names come from feature 1. Speak them as typed; if SAM mangles a name badly, that's
acceptable, don't build a pronunciation editor.

### Library: verify first

1. Find a JavaScript port of SAM published on npm. The likely candidate is **`sam-js`**
   (port by discordier, github.com/discordier/sam), which exposes a global `SamJs`
   with `new SamJs(options).speak(text)` and buffer methods such as `buf32(text)`.
   **Verify** the package name, its browser (UMD) file, the global it defines, and the
   API by reading its README and dist files before writing code.
2. It must load from an allowed CDN (`cdn.jsdelivr.net/npm/...` or `unpkg.com/...`),
   pinned to an exact version published at least two weeks ago. Add the `<script>`
   before the main inline script.
3. If no SAM port loads under those rules, **stop and tell the owner**, and offer the
   fallback below as the replacement.

### Behaviour

- Play SAM's audio through the existing Web Audio context in the `Sound` module
  (preferred: get a sample buffer from SAM and play it as an `AudioBuffer`), so voice
  respects the same user-gesture unlock.
- **Voice on/off** button next to "Sound on", separate setting, persisted as
  `voice: true|false` in `switchbox-settings`. Default **on**. Voice and Sound are
  independent switches: either can be on without the other.
- Never queue speech: if a phrase is still playing, drop the new one, except
  "game over", which cancels the current phrase and plays.
- Voice must not delay play. The computer opponent and animations keep their timing.
- If SAM fails to load or throws, fall back to the browser's built-in speech
  (`speechSynthesis`) with a low pitch (~0.5) and slow rate (~0.8), choosing an
  English voice. If neither is available, hide the Voice button.

## Tests to add (in a new `tests/t_players.py`)

- Names: setting a name updates the box label, status line, round table and verdict;
  empty input falls back to the default; names persist after reload; switching to
  the computer shows the computer's stored name.
- Colors: picking a color changes the box and the falling-ball color (read
  `COL.p[0]`); the other player's color is disabled; colors persist after reload.
- Voice: stub the speak function (`window.__spoken = []`) and check the right phrase
  fires for new game, a 4+ ball chain, round starts and game over; that nothing is
  spoken on ordinary turns; that the Voice button turns it off and the setting
  persists; and that no page errors occur when the SAM script is blocked (test the
  fallback by aborting the CDN route in Playwright).
- Re-run `t_suite.py` and `t_options.py`; the computer-opponent tests must still pass.

## Done means

- All three suites pass; one screenshot reviewed at desktop and phone width.
- The owner has heard SAM say the welcome line and approved how it sounds.
- Published to the existing artifact URL.
