# Freeciv45 civics: two ways to build them

Roadmap slice 8 of [freeciv45-plan.md](../../freeciv45-plan.md) ("Culture and civics") and part 4, second slice,
of [standalone.md](../standalone.md) (issue 274). The reference behaviour is [mechanics.md](../mechanics.md) 2.11:
a government made of several columns of choices, each with upkeep, so an empire is assembled from policies. The
plan proposed "governments plus one policy building per column that Lua swaps" and named the risk: "five columns
of exclusive choices are not native; the AI won't pick policies". Looking at the engine for this note turned up a
native alternative, so this note sets out both and asks John to choose before anything is built. Engine paths are
the patched tree at patch 0050.

## 1. What the engine has

| Piece | What it does | Evidence |
|---|---|---|
| Governments | One choice, with anarchy when it changes; civ45 has nine | `civ45/governments.ruleset` |
| Policies ("multipliers") | Named sliders a player sets, from `start` to `stop` in `step`s; an effect row with `multiplier = "<name>"` is scaled by the slider's value; a slider can have `reqs` (a tech, a government); a change takes effect at the next turn change | `data/civ54/governments.ruleset:470-530` and `data/civ54/effects.ruleset:950-958` (the only ruleset in the tree that uses them); `common/multipliers.h` |
| The Qt client's policy dialog | The "Policies..." menu entry opens a slider per policy; it is enabled only when the ruleset has any | `client/gui-qt/menu.cpp:1540, 2135, 3719`; `client/gui-qt/ratesdlg.cpp` |
| The AI and policies | Every turn it tries each slider a step down and a step up, rearranges its workers, and keeps the step if its cities' total want rises | `ai/default/daidata.c:440-475`, `dai_adjust_policies` |
| A requirement on a policy's value | None: there is no "Multiplier" requirement type, so an effect can only scale linearly with a slider, not switch on at one setting | the requirement types listed in `common/fc_types.h:770-900` |
| Lua and policies | No call reads or sets a slider | `common/scriptcore/tolua_game.pkg`, `server/scripting/tolua_server.pkg` (no "multiplier") |

## 2. Option A: policy sliders (recommended)

Each column is one native slider between two ends, and every step trades one thing for another. The player sets
them in the Policies dialog; the AI tunes its own every turn.

A first set, four sliders of five steps (0 to 4), each named for its two ends:

| Slider | Towards the right, per step | Cost per step | Available from |
|---|---|---|---|
| Labour: free to bonded | +5 % shields in every city | one more unhappy citizen in cities of size 6 and up | Bronze Working |
| Trade: open to guarded | -5 % waste of shields and gold by distance | -5 % gold | Currency |
| Faith: secular to devout | +1 content in cities that follow the state faith (religion.md) per two steps | -5 % science | Mysticism |
| Service: volunteer to levied | +1 free unit upkeep per city per two steps | -5 % luxury and +10 % war weariness | Feudalism |

The effects named are candidates: each must be checked against what Freeciv's effect types do with negative and
scaled values before it is built (for example, whether a negative `Make_Content` makes citizens unhappy, or
whether `Empire_Size_Base` is the better lever). The exact numbers come from balance games.

For it:
- native from end to end: the client already has the dialog, the AI already plays it, the save already keeps it,
  no Lua runs;
- every setting is a trade-off the player can tune, which no other game in the genre does this way (and so owes
  nothing to the reference's civic list);
- governments stay as they are, so this adds to the game without rebuilding it.

Against it:
- a slider is a dial, not a list of named choices, so it feels less like the reference's civics;
- effects are linear in the slider, so a setting can't switch something on (a free specialist, no anarchy) at one
  value;
- changing a slider has no anarchy and no cost beyond its effects, unless upkeep is added per step.

## 3. Option B: policy buildings (the plan's)

Each column has three to five named policies; each policy is a small wonder built in any city, with gold upkeep.
Building one makes Lua remove the column's other policy, and a hidden "Recently Reformed" wonder blocks another
change in that column for 10 turns.

For it:
- named, discrete policies like the reference's civics, each with any effects at all;
- the AI builds wonders by weighing their effects (`ai/default/daieffects.c`), so it would pick policies whose
  effects it values, with no new AI code;
- upkeep is native (`upkeep` of the building).

Against it:
- a policy is chosen by putting it in a city's production list and paying shields, not from a civics screen; a
  proper screen is client work (plan: "a client panel later");
- the AI can switch back and forth, paying shields each time, until the cooldown is tuned;
- small wonders are lost when the city holding them is captured, so Lua must move them to the capital (as
  religion.md 4.3 does for the state faith);
- four columns of four would add 16 buildings and their art.

## 4. The question for John

Option A (sliders) or option B (named policies as buildings)? Either can come after religion, resources and
cottages (#273, #276, #275) are in. With A, the first step is a test ruleset with one slider to confirm the effect
types behave with scaled and negative values; with B, it is the Lua for exclusivity and the cooldown, and a rules
test for both.
