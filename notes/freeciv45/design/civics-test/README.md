# Civics sliders: effect test (patch 0062, issue 274)

`civics.md` option A asked for a test first: do the effect types behave with scaled and negative values? This is
that test. Patch 0062 replaces civ45's two inherited civ54 sliders (Personal Freedom, Polluting Productivity) with
Labour, Trade, Faith and Service, each 0 to 4 with `factor = 50`. The three training-duration sliders stay.

## Method

1. Seed-7 AI game, 150 turns, with patch 0062 (`scripts/test.sh ... --turns 150 --ruleset civ45 --data
   port/s61/data:...`, log `logs/test-qt-20261024-124212`, not in git).
2. `variant.py` copies the turn-120 save with one player's four sliders set (value and target) and that player
   taken off AI control, so the AI can't re-tune them (`dai_adjust_policies` writes `value` directly:
   `ai/default/daidata.c:463, 485`).
3. `run.sh` loads each copy, plays two turns with `scorelog` on, and the player's score-log rows are compared.
   (`mfg` is the sum of city shield surplus and `techout` the sum of science, `server/score.c:297-299`.)
4. Where a penalty caused riots that hid a bonus, the run was repeated with a test copy of the ruleset with that
   penalty row removed ("no penalty" below). That copy is not shipped.

A slider whose tech the player lacks snaps back to 0 at turn end (`server/srv_main.c:1430-1438`), so each test
uses a player who knows the tech. Oscar II (no Feudalism) gave a false "no effect" for Service before this was
checked.

## Results (turn 122, the second turn after the load)

| Slider at 4 | Player | Expected | Seen | Verdict |
|---|---|---|---|---|
| Labour, shields (no penalty) | Mary Tudor | +20 % shields | mfg 39 → 42 | works |
| Labour, content | Mary Tudor | -2 content in every city | 1 city riots, unhappy 0 → 3 | works |
| Labour | Svend Tveskæg | both | 3 cities riot, mfg 85 → 69 | works; heavy if not offset |
| Trade, gold | Mary Tudor | -20 % gold | income +1 → -7 a turn | works |
| Trade, waste | Mary Tudor | -20 % waste | corruption 18 → 17 | works, small |
| Faith, science | Svend Tveskæg | -20 % science | techout 75 → 56 | works |
| Faith, content | Svend Tveskæg (state faith Hearth) | +2 content in state-faith cities | Labour 4 alone: 3 riots, 4 unhappy; Labour 4 + Faith 4: no riots, 0 unhappy, mfg 98 | works |
| Service, upkeep (no penalty) | Mary Tudor (Monarchy) | 2 more units per city free of gold upkeep | income +1 → +6 a turn | works |
| Service, luxury and unhappiness | Mary Tudor | -20 % luxury, +2 unhappy per aggressive unit | 1 city riots | works |

Each effect is scaled the same way: `(value * slider * factor / 100) / 100`, truncated per effect
(`common/effects.c:767-771`, `common/player.c:1969-1974`). So with factor 50, value 1 gives 0, 1, 1, 2 at steps
1 to 4, and value -1 gives 0, -1, -1, -2 (C truncates towards zero).

## Found on the way

- Under Despotism and Monarchy, civ45 units pay gold, not shields (`effects.ruleset`, `Shield2Gold_Factor` and
  the shield `Upkeep_Factor` that excludes both). A shield-only free upkeep did nothing there, so Service frees
  upkeep in shields and gold.
- `minimum_turns` restores a human player's slider to its default one turn after a change. The end-of-phase code
  treats "cannot be changed" as "requirements not met" (`server/srv_main.c:1430-1438`), and
  `multiplier_can_be_changed()` is also false during the lockout (`common/multipliers.c:141-145`). Upstream main
  has the same code. Only seen by reading the code, not in play (issue 320). The AI never hits the lockout, because it never
  sets `changed`. So 0062 sets no `minimum_turns`.
- In the 150-turn game the AI used Labour a lot (several civs at 4 by turn 120), and Trade and Service a little.
  It never used Faith. Whether Faith's science cost is too steep belongs to the pacing games (issue 284).

## Not checked

- The Qt Policies dialog with the new sliders (the client reads them from the ruleset like any other).
- The other end-of-game numbers; the 150-turn game's city counts (50, 108, 113 at turns 50, 100, 150) match the
  0061 game (51, 107, 112).
