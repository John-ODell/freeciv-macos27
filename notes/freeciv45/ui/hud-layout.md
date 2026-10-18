# Freeciv45 HUD: what goes where

Date: 2026-10-17. Source: John's reading of a modern 4X's screens, kept in the local, git-ignored
`mapset_refs/` folder and described here in words. The clean-room rule stands: nothing in that folder is a
visual reference for art or for the look of our widgets; this note only records which information the player
sees, where the controls sit and how the screens connect, so our own design (`panels.md`) has one list of
requirements. Freeciv45's visual style is its own (plan row Q1 to Q3, `panels.md` section 4).

## 1. Persistent regions of the main screen

| Region | Shows | Freeciv Qt today | Freeciv45 |
|---|---|---|---|
| Top strip, full width | Empire numbers at a glance, each with an icon and a per-turn delta: research rate, gold and income, happiness, culture total against the next threshold, faith, then the strategic resources owned with counts; far right the turn number and year, help and menu | `top_bar` with gold, tax rates, research as text buttons; turn done elsewhere (`qt-today.md` section 2) | One strip, same facts, deltas in brackets, resources only once the ruleset has them (slice 4); click a number opens its overview |
| Bottom left | The selected unit's card (section 2) | Unit info widget, text heavy, fixed | `panels.md` section 2: the unit bar, first slice built (`first-slice.md`) |
| Bottom right | Minimap with overlay toggles; directly above it one big call-to-action button for what the turn needs next (choose production, choose research, unit needs orders, end turn) | Minimap; turn done button in the top bar; messages window separate | Keep the minimap; add the single "what next" button above it that cycles through blocking items and becomes End Turn when nothing blocks |
| Right edge, vertical | A column of round buttons: overview screens (section 4) at the top, then the notification stack (section 5), then the "what next" button | Nothing comparable; messages are a dock widget | Column of round buttons, notifications as badges, see section 5 |
| Left edge, vertical | A short column of unit action icons next to the unit card (attack, fortify, sleep, alert, skip) and a collapse arrow | Actions live in menus and keyboard | Folded into the unit bar's action row (`panels.md` section 2.4) |

## 2. The selected unit card (bottom left)

Appears when a unit is selected, hides when nothing is. Contents, top to bottom:

- A title bar with the unit name and two arrows that cycle to the previous and next unit that still needs
  orders this turn. The arrows are the main way a player gets through a turn.
- A round portrait with a health bar under it, and the unit's promotion or veteran marks as small badges to
  its right (one filled badge per level, a star-like badge for the top level).
- Two numbers with labels: movement as "left / max" with a small go-to arrow, and strength with a shield badge.
- A collapse arrow so the card can shrink to the title bar.

Freeciv45 mapping: already the shape of `panels.md` section 2. Add the previous/next-unit arrows to the title
(Freeciv has the focus-cycling logic; the client's "W" wait and "Space" done keys map to them), and show the
veteran level as badges rather than text.

## 3. The city view as a map overlay, not a dialog

Clicking a city does not open a window over the map; the map stays, centred and zoomed on the city, the
surrounding worked tiles show their yields as small icons on each tile, the owned area is outlined, and panels
sit on top of the map's edges:

- Top left: citizens count, turns until the next citizen, then the per-turn yields with icons (food,
  production, gold, science, faith, culture), each with its sign; under them a culture-border progress ring.
- Top centre: the city name with previous/next-city arrows, the city's defence strength badge above it, status
  icons (unhappy, resources, connections) under it, and an Edit for the name.
- Bottom left: current production: item name, production per turn, a portrait, cost and maintenance, the
  effect text, a scroll for the description; above it two buttons, Purchase (with gold or faith) and Change
  production; a Show queue toggle.
- Right: a tall panel of collapsible sections: citizen management (manual specialist control toggle),
  great people with one progress bar per kind, specialist buildings (each with its specialist slots shown
  as small yield icons), buildings (name and icon per row). The sections collapse so the list stays short.
- Bottom centre: the rare actions (raze), buy a tile, and Return to map.
- Hovering a tile shows the same tile tooltip as on the main map (section 6).

Freeciv Qt today: a full city dialog window with tabs (`qt-today.md` section 3). Freeciv45: `panels.md`
section 3 proposes a side panel opened from a round city marker; this section says what goes in it and
confirms the decision John leaned to in chat: the city is inspected on the map, with the full dialog kept
reachable for the rest (decision 15). The worked-tile yields on the map are the client's existing citizens
overlay ("city output" view option) drawn in the new style.

## 4. Overview screens behind one menu

One button on the right edge opens a short list of overview screens: demographics, diplomacy, economy,
espionage, military, notification log, religion, tech tree, victory progress. Each opens as a large modal
panel over a dimmed map with a Close button at the bottom, so the player never leaves the map's context.
Separate round buttons beside it open the ones used every few turns: diplomacy, research, the policy tree,
the civilopedia equivalent, and the two advisor buttons that light up when something needs attention.

Freeciv Qt today: these are top-menu entries and separate windows (Research, Players, Cities, Economy, Units
reports; Freeciv's Help). Freeciv45: group them under one round button, open each as a modal over the dimmed
map, keep the menu bar entries as the keyboard path.

## 5. Notifications

Events arrive as a vertical stack of round badges on the right edge (an exclamation badge over an icon for
the kind: city, diplomacy, military). Clicking one jumps to the thing and dismisses the badge; the full list is
the notification log overview. Nothing scrolls past the player in a text window.

Freeciv Qt today: the messages dock, a scrolling text list (`qt-today.md` section 2). Freeciv45: badges on
the right edge fed by the client's existing message events (each already carries a tile or city to jump to),
with the messages dock kept as the log.

## 6. Tile information

- Hovering a tile shows a compact dark box near the cursor: the units on it (owner, type, strength), the
  owner and city of the tile, improvements and routes, terrain and features, the yield as icons with numbers,
  fresh water or other notes. This is plan row Q2's hover summary.
- A persistent small box above the minimap repeats the hovered tile's improvement, terrain and yield so the
  cursor box can be short.
- City banners on the map: size, name, the production item's icon, a defence strength badge above, and thin
  growth and production progress bars. Unit flags: a round badge with the unit type, a strength number, and
  a count when stacked.

Freeciv Qt today: a tooltip exists for tiles and the city bar shows size, name and production text. Freeciv45:
the richer tooltip (Q2) and badge-style banners drawn in the test tileset's style once T1 exists.

## 7. Later screens, recorded for the slices that need them

- **Policy tree (slice 8, civics):** a modal grid of branches, each a card with a title, an Adopt button and
  a small tree of five or six policy icons connected by lines; a footer with the next policy's cost, culture
  per turn, turns to the next policy, and a progress bar toward the culminating project. Freeciv45's civics
  are governments plus policy buildings (plan row 8); this is the screen that would present them.
- **Espionage overview (civ54 or later):** a table of agents with name, rank, location, activity and
  View/Move buttons, beside two sorted tables of own and foreign cities with a potential rating. Freeciv45's
  first playable has no espionage points; the Spymaster uses native diplomat actions (decision 14).

## 8. What this changes in panels.md

Folded into `panels.md` on 2026-10-17 (issue 118): item 1 in its 2.3, item 2 in its section 3, items 3 and 4 in
its new section 8, and the mockup redrawn with a map frame and a city frame.

1. Add the previous/next-needing-orders arrows to the unit bar's title.
2. The city panel becomes a map overlay set (left yields, right collapsible sections, bottom production), not a
   single side panel; the round marker still opens it.
3. New: the top strip with empire numbers, the right-edge button column with overviews and notification
   badges, and the single "what next" button above the minimap.
4. The tile tooltip (Q2) gets a persistent twin above the minimap.
