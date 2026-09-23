# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Mind Kids is a Telegram Mini App with 37 brain-training games for children aged 4–12. The whole app is one file, `mind-kids.html` (inline CSS and JS). It has no build step, no dependencies, and no package.json. The only external script is `telegram-web-app.js`. The app also runs in a plain browser: `inTg` is false there, and storage falls back to localStorage. The repo also contains `bot/` (an aiogram Telegram bot, deployed to Hetzner) that opens the mini app, which itself is deployed to Vercel via `vercel.json`.

## Commands

```bash
node scripts/check-i18n.js     # I18N uz/ru key parity + placeholders, LX word lists, COLORS, SHAPE_N, all 37 def() have uz+ru name/desc
node scripts/check-age-cfg.js  # AGE_CFG difficulty table (games 31-37) in bounds for every age x level 1..10
python -m http.server 8765     # serve locally; open http://localhost:8765/mind-kids.html (Playwright blocks file://)
pip install -r bot/requirements-dev.txt; pytest bot/   # bot tests (local venv: bot/.venv)
pytest bot/test_bot.py -k stats                          # single test / subset
powershell -File deploy/deploy.ps1 -StageOnly            # dry run: print what would be shipped, no ssh
powershell -File deploy/deploy.ps1                       # deploy bot to Hetzner (root@178.104.103.113)
```

The check scripts read `mind-kids.html` as text and `eval` object literals out of it by matching markers such as `const I18N=`, `const AGE_CFG={`, `const COLORS={`, `const SHAPE_N={` and `def({name:{uz:`. If you rename or reshape these, the scripts break.

To syntax-check the JS, extract the inline `<script>` block to a temporary file and run `node --check` on it.

The mini app has no test runner. Its behaviour is verified in a browser. Top-level `const`s and functions (`S`, `G`, `openGame`, `closeGame`, `makeApi`, `Voice`, `Snd`) are reachable from `page.evaluate`, so game flows can be driven programmatically.

## Code style

The JS is written deliberately dense: long one-liners, short names (`S`, `G`, `R`, `ri`, `$`) and almost no comments. Match this style and do not reformat.

The file is organised into banner sections of the form `/* ================= Name ================= */`, in this order: Telegram & platform, Random helpers, i18n, Shared data, Engine, Stats, Games, Age-scaled difficulty, Home, Parent panel, Wiring.

## Architecture

**Game registry.** `def({...})` pushes each game into `G`, and its id is its 1-based position in `G`. Stats are keyed by id, so new games are always appended at the end and existing games are never reordered. Each game has `name`/`desc` as `{uz,ru}`, `age` (`'4-6'|'7-9'|'10-12'|'all'`), `cat`, `icon`, `art` and `sk` (skills), plus exactly one of the following:

- `gen(L)` is a multiple-choice game. It returns `{prompt, say?, board?, options[], answer?(default 0), fixed?, cols?, cls?, time?, key, explain, after?}`. The engine's `playChoice` renders it, shuffles the options unless `fixed` is set, and grades the answer. `key` is used by `fresh()` to avoid repeating a question within a session and across the last 50 questions (`mk_seen_<id>`).
- `mount(a)` is a custom game that renders into `a.board` and uses the API from `makeApi(tok)`:
  - `a.prompt(html, say)`, `a.hint(t)`, `a.done(ok, {msg, bonus})`;
  - `a.miss()` takes a life and returns true when lives reach 0;
  - `a.later` and `a.every` (auto-cancelled, `live()`-guarded), `a.on` (auto-removed listener), `a.timer(sec, onEnd)` and `a.fresh(fn)`;
  - `a.L` (level 1–10), `a.age`, `a.lang()`.

**Round lifecycle and the `S.tok` guard.** `S` holds all game state. `startRound()` calls `cleanup()`, increments `S.tok`, and runs either `playChoice` or `mount`. Every async callback captures the token and bails out if `tok!==S.tok`. Always register timers through `S.timers`/`S.ints` (or `a.later`/`a.every`) and check the token, otherwise a stale timer can leak into the next round or game.

`finishRound(tok, ok, o)` scores the round, then auto-advances via `nextRound()` after `OK_ADVANCE_MS` or `WRONG_ADVANCE_MS`. There is no "continue" button. `nextRound()` calls `endGame()` when lives reach 0 or the player passes level 10.

Lives: there are 3 per game. `S.rl` counts lives lost in the current round, so if `a.miss()` already took a life, `done(false)` does not take a second one.

**Age.** `S.age` is the effective age: `g.age`, or for `age:'all'` games (ids 31–37) the home filter or an age-picker dialog (remembered in `mk_age`). Games 31–37 read their difficulty from the `AGE_CFG[game][age]` table and interpolate with `lerp(min, max, L)`. Put new difficulty numbers in `AGE_CFG`, not inline.

**i18n.** `LANG` is `uz` (default) or `ru`.
- `tr(key, params)` reads UI strings from `I18N`. Static DOM text uses `data-i18n` and `data-i18n-aria`, filled by `applyI18n()`.
- Game content uses `{uz, ru}` objects resolved with `loc(v, lang)`. Language-specific content (alphabets, similar letters, word lists) lives in `LX[lang]`.
- English exists only in game 32 (Stroop), which has its own language in `mk_lang_stroop`. `curLang()` returns that language while game 32 is open.
- Every UI key must exist in both `uz` and `ru`; `check-i18n.js` enforces this.

**Voice.** `Voice.say` uses Web Speech and picks an uz voice, falling back to a tr voice. Prompts are spoken automatically only when `S.age==='4-6'`, and at most once per lang+text per game session (`S.spoken`, reset in `openGame`). The 🗣 button always speaks.

**Persistence.** `Store` writes to localStorage and mirrors to Telegram CloudStorage (Bot API ≥ 6.9); `get` waits for the cloud value but falls back to the local one after 1.5 s. All keys are prefixed `mk_`: `mk_stats` (the `ST` object with per-game `per[id]`), `mk_seen_<id>`, `mk_age`, `mk_lang`, `mk_lang_stroop`, `mk_theme`, `mk_filter`, `mk_snd`.

**Theming.** Colours are CSS tokens on `:root`, overridden under `:root[data-theme=dark]`. Use the tokens (`--brand`, `--ok`, `--bad`, `--card`, …) and never hard-coded colours.

## Bot and deployment

**Mini app (Vercel).** `vercel.json` rewrites `/` to `/mind-kids.html`, so the file keeps its name (the check scripts also depend on it). `.vercelignore` keeps `bot/`, `deploy/`, `docs/` and `scripts/` off the public site. There is no CSP header, because the page relies on inline script and style. Live URL: `https://mind-kids.vercel.app`.

**Bot (`bot/`, @MindKidsUzbot).** It uses aiogram 3 with long polling and is modelled on the Dunyo Hotel mini-app bot.
- `/start` sends the welcome photo with an inline `web_app` button. The photo's `file_id` is cached in memory after the first upload.
- On startup the bot also sets the chat Menu Button to the mini app.
- `/stats` is registered with an `is_admin` filter. A non-admin's `/stats` falls through to the catch-all fallback, so the command is never revealed.
- `bot/db.py` (aiosqlite) stores only `user_id`, `first_seen` and `last_seen` in UTC. "Today" in the stats means Tashkent time (UTC+5).
- Replies are Uzbek only, via `TEXTS["uz"]` in `bot.py`, which is kept as a dict so `ru` can be added.
- The mini app never sends data to the bot: there is no `sendData`.

**Server.** The host (Ubuntu, Python 3.14) is shared with about 9 other bots. Ours uses the `mindkids-bot.service` unit, the `/opt/mindkids-bot` directory and the non-root `mindkids` user. Never touch other units.
- `deploy/install.sh` runs on the server and is idempotent. It never writes `bot/.env` (mode 600, holds `BOT_TOKEN`, `WEBAPP_URL`, `ADMIN_ID`) and never touches `bot/data/` (the SQLite DB).
- `deploy.ps1` retries ssh and scp, because the connection to this host intermittently resets new SSH connections before the banner (exit 255).
- Windows PowerShell 5.1 strips embedded double quotes from arguments passed to `ssh`. Remote commands that contain `"` break, so use single quotes or run them inside an interactive session.
- Logs: `journalctl -u mindkids-bot -f`.

## Specs

Feature work starts from a spec in `docs/specs/` (written in Uzbek, EARS-style rules plus acceptance criteria). Read the relevant spec before changing its area:
- `new-games-integration.md` covers games 31–37 and `AGE_CFG`;
- `i18n-ru-en.md` covers languages;
- `round-flow-autoadvance.md` covers round end and voice.
- `telegram-bot-deploy.md` covers the bot, Vercel and Hetzner deploy.
