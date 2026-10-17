# The harness hook: an outside chooser for an AI player (issue 62, 2026-10-16)

Patch 0007 lets a program outside Freeciv make two of the default AI's choices for named AI players: what each
city builds, and what to research. It was written for the play harness that John's other desks are building
(the shared repo John-ODell/qwen-play-harness), where a model answers numbered menus. John's go-ahead: "Yes, go
with the AI-asks hook: open the issue and build it with a random chooser. No model runs until the shared core and
the Mac lock exist." No model has been run. Everything below was tested with `scripts/harness-chooser.py`, which
answers at random or always takes the AI's own pick.

Line numbers are for the fork at patch 0007 (commit `ad3099a`, upstream S3_2 `44e6898` plus patches 0001 to 0007).

## Why Freeciv needs a hook

- Lua can read the research (`researching`, `researching_cost`, `common/scriptcore/tolua_game.pkg:211-214`) and
  add bulbs (`Player:give_bulbs`, `server/scripting/tolua_server.pkg:389`), but neither API file has a way to set
  the research or a city's build (observed: no production or research setter in either `.pkg`).
- The default AI decides both again for its players every turn. At the end of each phase the server calls the AI's
  `last_activities` (`server/srv_main.c:1483`), which is `dai_do_last_activities` (`ai/default/aihand.c:774`). That
  runs `dai_manage_cities` (`:785`) and `dai_manage_tech` (`:788`) before the cities produce
  (`server/srv_main.c:1518`). Whatever a script set during the turn would be decided over by the next AI pass
  (derived).

So the hook sits inside the AI's own two decisions. The AI still computes its choice, and the hook asks the
chooser first.

## Turning it on

| Variable | Meaning |
| --- | --- |
| `FREECIV_HARNESS_DIR` | Directory for the exchange files. Unset or empty: the hook is off and the server behaves as before. |
| `FREECIV_HARNESS_PLAYERS` | Comma-separated names of the players whose choices go to the chooser (case-insensitive). Required. |
| `FREECIV_HARNESS_TIMEOUT` | Seconds to wait for each answer, default 60; 0 never waits, which records the questions only. |

The variables are read once, on the first AI pass (`harness_load`, `ai/default/daiharness.c:119`). The server log
then says `harness: on for Tested; files in DIR; an answer may take up to 60 s.`. Mistakes are logged and leave the
hook off: the players variable missing or empty, or a directory it can't write in. A listed name that is no player of
the game, or a player that isn't AI-controlled, is logged once (`harness: there is no player named X.`,
`harness: X isn't AI-controlled, so it isn't asked.`). Only AI players are asked: a human player's choices are never
taken over.

## The files

All three live in `FREECIV_HARNESS_DIR`. On start the hook removes a leftover `question.json` and `answer.txt`.

- `question.json`: one question at a time. It is written to `question.json.tmp` and renamed, so a reader never sees
  half a file, and it is removed once the question is settled (`harness_ask`, `:428`). Fields: `id` (1, 2, 3, ... per
  server run), `game` (`"freeciv"`), `ruleset`, `turn`, `year`, `player`, `kind` (`build` or `research`), `reason`
  (see below), `city` (null for research), `question` (one sentence of context), `options` (2 to 8, each with `n`,
  `label`, `value`, the rule name, and `ai`, true only for option 1, the AI's own pick) and `state` (the status page).
- `answer.txt`: the chooser writes one line, `ID CHOICE`, for example `7 2`, best written to a temporary file and
  renamed. Anything after the two numbers is ignored (`sscanf`, `:498`), so a chooser may append its reason there; the
  hook doesn't record it. An answer for another id is logged and dropped. A line that isn't two numbers, a choice
  outside 1 to N, or no answer within the timeout keeps the AI's pick (the "fallback").
- `applied.jsonl`: the hook's own record, one line per question:
  `{"id", "turn", "player", "kind", "reason", "city", "options", "choice", "value", "ai_value", "fallback", "secs"}`.
  A pick with only one option is applied without a question, so it gets no id and no line.

While it waits the server does nothing else, so the hook is for autogames (`-e`, `timeout -1`, no clients). Each
decision is also one server log line, for example
`harness: q3 turn 6 Tested build Stockholm: 7 options, fallback to 1 (Settlers): timeout`.

A question from the test (`id` 7, options 5 and 6 and most of the status page left out):

```json
{"id": 7, "game": "freeciv", "ruleset": "Freeciv45 ruleset", "turn": 26, "year": -2750, "player": "Tested",
 "kind": "build", "reason": "converting", "city": "Stockholm",
 "question": "Stockholm (size 2) has been on Coinage for 5 turns. Its shields go into Coinage, so nothing is being built. What should it build next?",
 "options": [
  {"n": 1, "label": "Settlers (unit, 30 shields, 10 turns; attack 0, defence 1, moves 1)", "value": "Settlers", "ai": true},
  {"n": 2, "label": "Coinage (converts the city's shields; nothing is built)", "value": "Coinage", "ai": false},
  {"n": 3, "label": "Barracks (building, 30 shields, 10 turns; upkeep 0 gold)", "value": "Barracks", "ai": false},
  {"n": 4, "label": "Aqueduct, River (building, 20 shields, 7 turns; upkeep 0 gold)", "value": "Aqueduct, River", "ai": false}],
 "state": "Turn 26 (2750 BCE). You are Tested, leader of the Swedes; government: Anarchy.\nGold 102 (+3 a turn). ..."}
```

## When it asks

Between decisions the chooser's pick stays. For a listed player's city the AI's pass returns early unless a
decision is due (`ai/default/daicity.c:266-270`), the same way it already does for a player who is away
(`:259-264`).

A city's build is due (`harness_build_reason`, `daiharness.c:606`) when:

| Reason | When |
| --- | --- |
| `new` | The hook has no pick for the city yet: just founded, captured, or the first pass after the server started. |
| `finished` | The city completed a build since the last pick (`turn_last_built` changed). |
| `changed` | Something else changed the build, for example the server when a target can no longer be built. |
| `danger` | The AI rates the city in danger (`urgency` above 0), asked only if the AI would build something else. |
| `converting` | The city has been on Coinage for 5 turns since the last pick, asked only if the AI would build something else. |

Coinage needs its own rule because it never finishes. The server turns its shields into gold and repeats it
without touching `turn_last_built` (`server/cityturn.c:2612-2627`; `turn_last_built` is set at `:2673` only when a
building is built). Without the rule, the first test's Stockholm stayed on Coinage from turn 21 to the end.

When a build is due, the AI computes its choice as usual. Just before it would change the build, the hook puts the
menu to the chooser (`dai_harness_choose_build`, `daiharness.c:858`, called at `daicity.c:355-358`). With only one
option there is nothing to ask, and the pick is recorded without a question.

The research is due (`dai_harness_research_due`, `:910`) the first time (`first`), after every new tech
(`discovery`), and when something else changed it (`changed`). The hook remembers a pick per research, not per
player, so teammates who pool their research (the default) are asked once between them. The hook replaces the AI's
own switch rule (`ai/default/aitech.c:362-374`); the AI still sets its long-term tech goal. A pick made on the turn
after a discovery loses nothing. The server keeps the bulbs left over from the discovery as free bulbs
(`server/techtools.c:411-415`) until just after the AI pass (`server/srv_main.c:1489`), and `choose_tech` charges
`techpenalty` only on bulbs beyond those (`server/techtools.c:1046-1059`). A `changed` pick in the middle of a tech
pays the usual penalty (derived from the same lines).

Everything else stays with the AI: unit moves, city sites, workers, taxes and rates, government, diplomacy and war.

## The menus

Build (`harness_build_options`, `:754`), at most 8, each one the city can build now, no repeats:
1. the AI's pick;
2. the current build;
3. the two buildings the advisor wants most (`building_want` above 0);
4. the best defender, then a city founder, a worker and the best attacker;
5. the rest of the buildings, most wanted first.

Labels give the cost and turns, plus attack, defence and moves for units and gold upkeep for buildings. Coinage's
label says it converts the shields.

Research (`harness_research_options`, `:995`): the AI's pick first, then every tech that can be researched now, in the
AI's own order of value, 8 at most. Labels give bulbs, turns at last turn's rate (left out when no bulbs came in) and
up to four things the tech leads to: units, buildings, then techs.

The status page (`harness_status`, `:328`) has the same layout for every question: turn and year, leader, nation and
government; gold, income, rates and score; research and bulbs; one line per city (surpluses, build and progress,
citizens' moods, units there, enemy units within 3 tiles); unit counts by type; other players and the diplomatic
state with each.

## Testing

`scripts/harness-test.sh ~/freeciv-builds/qt` plays a 50-turn civ45 game on a small map. It has one created AI
player, Tested, and two more from aifill, with seeds 7 and 7. The hook is on for Tested and
`scripts/harness-chooser.py` answers. The chooser leaves question 3 unanswered and answers question 5 with an option
that doesn't exist, so both fallbacks run, with a 3-second timeout. `scripts/harness-check.py` then checks:

- `decisions`: ids 1 to N, both kinds, all for Tested.
- `questions`: a copy of every question, 2 to 8 numbered options, the AI's pick first and only there, no repeats,
  and a status page.
- `answers`: each applied choice is the chooser's, and the two fallbacks kept the AI's pick.
- `saves`: in every autosave (start of turn, before that turn's decisions), each last pick is still in place, or
  the game changed it and the hook asked again that turn. Every city a decision names is in a later save under the
  same name.
- `re-asks`: at most a quarter of the decisions come from the game changing a pick.
- `game`: the game-over save is at turn 51.

A control game on the same seeds, without the variables, must end without a single `harness: ` line. Tested's final
score in both games is printed, not checked. `--mode first` makes the chooser always take the AI's pick.

| Run (2026-10-16, `logs/`, git-ignored) | Decisions | Builds | Research | Score with hook | Score in control |
| --- | --- | --- | --- | --- | --- |
| random, `harness-civ45-20261016-195835` | 20 | 16 | 4 | 24 | 23 |
| AI's pick, `harness-civ45-20261016-195851` | 19 | 13 | 6 | 23 | 23 |

Both passed every check. Each 50-turn game took about 10 seconds; every answered question took under a second
(`secs` 0) and the unanswered one the full 3. Reasons in the random run: 10 finished, 5 new, 3 discovery, 1 first,
1 converting; no `changed` or `danger`. One score per run on one seed says nothing about strength yet.

## Found while building it

1. Coinage never finishes, so a city the chooser put on it was never asked again (first run). The `converting` rule
   fixed it, and the next run had 20 decisions instead of 13.
2. City names with accents lost their letters in the JSON (`Lödöse` came out as `Ldse`). In 3.2, `fc_strlcpy`
   copies through ICU, which drops invalid UTF-8 (`utility/support.c:791-830`), and `astr_add` copies with it
   (`utility/astring.c:258`). The JSON writer added one byte at a time, so each half of a two-byte letter was dropped.
   It now copies text in runs (`harness_json_string`, `daiharness.c:240`). The checker had missed it because it
   skipped save cities no decision named; it now matches every named city against the saves.
3. Research labels at 0 bulbs a turn read "about never at this rate"; the turns are now left out then.
4. The control check counted the word "harness" in the log, which also matched the log folder's name in two paths.
   It now counts `harness: `.
5. The review found that the hook remembered research picks per player. Two named teammates sharing a research
   would each have seen the other's pick as a change, and asked again every turn, paying the switch penalty each
   time. Picks are now kept per research (`research_number()`), in an array sized for player and team slots
   (`common/research.c:51`).
6. The checker reported the two fallbacks as tested even in a game too short to reach question 5. It now fails then
   (checked with `--turns 5`: 2 decisions, `answers: FAILED, no question 3,5 to test a fallback on`).

## Limits

- Builds and research only. City sites and war or peace, which the PM's first plan also listed, would need hooks
  of their own.
- A long build is asked again only when it finishes or the game changes it.
- A city in danger is asked every turn while the AI would build something else, so a war can bring a question per
  city per turn.
- With pooled research, a named player's teammates should be named too: an unnamed teammate's AI can change the
  shared research, and the named player is then asked again (`changed`).
- The picks live in the server's memory. A game loaded from a save asks about every city and the research again
  once.
- One question at a time per server. With several players named, their questions take turns.
- The server waits on every question, up to the timeout. With a model at the PM's 4.4 s median, 20 decisions add
  about a minute and a half to a 50-turn game (derived).
- 20 decisions in 50 turns on a size 2 map is under the 40 to 80 a game this desk estimated in its reply to the PM.
  A bigger map or a longer game would give more; that is the harness's call.

## For the play harness

The question is already the shape the harness core wants: a numbered menu, the built-in AI's pick as option 1
(the "built-in" baseline), and a status page. A Freeciv adapter only has to watch for `question.json`, pass it to the
core's chooser and write `ID CHOICE` to `answer.txt`. `applied.jsonl` is the server's side of the record, against
which the core's own log can be checked. The adapter belongs in this repo and the core in qwen-play-harness, as
agreed with the desks; neither exists yet.
