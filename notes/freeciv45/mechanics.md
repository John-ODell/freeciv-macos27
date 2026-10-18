> Research record of 2026-10-16, from public secondary sources only, written while slice 1 (PR 47) was changing
> civ45. Since then: open question 1 is settled (civ45 is Freeciv45, with stacks on a square map; the hex and
> one-unit-per-tile rules are civ54), and the "culture-driven borders already working in civ45" of 2.13 was the old
> slices' city radius that grew with culture (`notes/civ45-planning.md:95`), which patch 0006 removed. Checked
> against the 3.2 source on 2026-10-16: Lua can cut a unit's hit points, and the cut kills at zero
> (`server/scripting/api_server_edit.c:592-598`), after an attack (`action_finished_unit_units`,
> `server/scripting/script_server.c:542`), but it cannot read them (no hit point field in
> `common/scriptcore/tolua_game.pkg:58-66`), so Lua collateral cannot be kept non-lethal and the plan keeps siege
> on the native Bombard action. No Lua edit call changes a city's size or shield stock
> (`server/scripting/tolua_server.pkg:118-250`). An Extra requirement reaches TradeRoute range at most
> (`common/requirements.c:1214-1217`), not the city range 2.2 says, but still not Player, so its conclusion holds.
> Names of the reference game's civics, traits, promotions, units and wonders appear here only to describe it;
> Freeciv45 uses names of its own. Plan: `notes/freeciv45-plan.md`.

# How Civilization IV: Beyond the Sword plays: a clean-room description for civ45

Written 2026-10-16 for civ45, a GPL-2.0-or-later ruleset on Freeciv 3.2 (repository John-ODell/freeciv-macos27).

## Method, labels and disclosure

- **Sources.** Only public secondary sources: community wikis, strategy articles, forum guides and reviews (S1 to S79). Remarks on how well Freeciv fits cite Freeciv's own GPL source (S80 to S99) and the project's public notes (S100, S101). No Firaxis or 2K material was opened: no game files, data, SDK, art, manuals or Civilopedia text, nothing in Steam's folders, and no reverse-engineering tools.
- **Own words.** All text is mine. There are no quotations and no copied stat tables; numbers appear only as single rule values, patterns or ranges.
- **Labels.** Every claim carries a label and a source tag. O = observed (the cited source states it), D = derived (follows from cited facts), I = inferred (my judgement). "(O S32)" means observed in source S32; the URLs are in section 5. Every MUST, LATER or SKIP rating is inferred.
- **Numbers** are for normal game speed and the final BTS patch, as the sources report them. Where sources disagree, the text says so.
- **Disclosure.** The Fandom "Combat (Civ4)" page appeared to contain in-game (Civilopedia-style) help text. It is not cited and nothing here depends on it; combat facts come from other sources, chiefly S5, S14 and S32 to S49. The other Fandom pages were read with their Civilopedia, quote and history sections skipped.

## 1. Top 12 differences from Civ2 and stock Freeciv

Freeciv's default rules follow Civ2 (O S78), so the comparison below is mostly against Civ2-style rules.

1. **One strength number.** A unit's single strength, shifted by percentage modifiers, sets both each round's odds and the damage per hit, so small edges compound (O S32, S33); Civ2 and Freeciv split attack from defence and deal a fixed amount per round (O S77, S83).
2. **Stacks where only the loser dies.** The best-matched unit defends, only the loser of the duel dies, siege spreads non-lethal collateral damage and mounted units flank, so armies become mixed "stacks of doom" (O S32, S34, S37, S42); in Civ2, and in Freeciv's default killstack, the whole stack dies outside cities and fortresses (O S77, S80, S81).
3. **Chosen promotions.** XP buys a promotion the player picks from branching lines, and fighting produces Great Generals (O S43, S44, S45); Civ2 has one veteran step and Freeciv a linear, chance-based ladder (O S77, S87).
4. **An empire-wide resource network.** A resource inside your borders, improved and linked by road, river or coast, serves every connected city, gating units and lifting happiness and health caps (O S13); a Freeciv extra only counts in requirements up to city range (O S86).
5. **Gold maintenance instead of corruption.** Each city costs gold that grows with city count and distance to the palace, units cost gold, and Civ2-style corruption is gone (O S7, S8, S28, S29).
6. **Soft caps on city size.** Citizens above the happiness cap stop working but still eat, and each point of unhealthiness costs food; cities do not riot from unhappiness and there are no pollution tiles (O S7, S19, S20).
7. **Population as currency.** Cottages grow into towns while worked, and slavery or the draft turns citizens straight into hammers or units (O S15, S21, S22).
8. **Seven interchangeable religions.** They are founded by the first civ to a tech, spread by trade and missionaries, pay in happiness and shrine gold, and drive early AI friendships and feuds (O S53, S67).
9. **Civics, not governments.** Five columns of five options are mixed and matched, each with an upkeep, and switching costs anarchy (O S55, S56, S57).
10. **Great People and golden ages.** Specialists and wonders produce Great People who settle as super-specialists, discover techs, rush builds, build shrines or start golden ages (O S50, S52).
11. **Culture with teeth.** City culture levels push borders, add city defence, can flip a rival's city and can win the game (O S38, S61, S72).
12. **Readable leaders.** Each leader has two traits and an AI personality, AI attitude is a visible sum of modifiers, many of them remembered deeds, and BTS adds vassals and Apostolic Palace and UN votes (O S54, S58, S68, S69, S75).

## 2. Systems

### 2.1 Map

The world is a grid of square tiles, and a unit can step to any of its eight neighbours, a diagonal step costing the same as a straight one (O S1, S10). A city works a "fat cross": the 5-by-5 block around it minus the four corners, 21 tiles counting the centre, and that radius never grows (O S11). Citizens can only work tiles inside the cross (O S13), so neighbouring crosses compete for land and city spacing is a core decision (I). Six standard map sizes run from Duel, about 1,000 tiles for 2 civs by default, to Huge, about 10,000 tiles for 11 civs (O S12), and each step up adds roughly 50 to 75% more tiles (D from S12). A fixed, readable grid suits Civ4's careful empire planning (I).

**Rating: MUST.** Topology and map size are stock Freeciv server settings that a ruleset can preset, and the city radius is ruleset data (O S80, S88), and a fixed squared radius of 5 covers exactly the 21-tile cross (D). This conflicts with civ45's current hex slices (D from S100, S101; see open question 1).

### 2.2 Land: terrain, features and resources

Each terrain gives a base mix of food, hammers and commerce, and features such as forest, jungle, flood plains and oases change yields, movement and health (O S13, S20). Terrain also defends: forest and jungle add about 50%, hills 25%, a forested hill 75%, and an attacker crossing a river is penalised (O S14). Rivers add commerce, supply fresh water for farms and health, and serve as trade links (O S13, S20, S26). Resources fall into three families: luxuries add happiness, food resources add health, and strategic resources unlock units and some buildings (O S13). A resource counts only when it lies inside your borders, has the right improvement and links to your cities by road, river or coast; then every connected city shares it (O S13). Spare copies are traded between civs (O S67), which makes resources constant diplomatic currency (I).

**Rating: MUST.** Resources gate both the roster and the city caps (I). Freeciv terrains, features and resource extras express yields and per-city bonuses, but an Extra requirement reaches at most city range (O S86), so empire-wide access needs Lua, for example a turn-start script that grants a hidden national marker building for each resource the player can reach (I; the turn signal and building calls exist, O S93, S95).

### 2.3 Tile improvements

Workers build farms for food, which need fresh water or a chain of irrigated tiles that later techs loosen, mines on hills for hammers, and workshops that trade food for hammers (O S13, S14). Watermills on rivers and windmills on hills mix food, hammers and commerce, and lumbermills add hammers while keeping the forest (O S13). A cottage grows only while worked: it becomes a hamlet, a village and then a town, rising from 1 to 4 commerce after about 10, 20 and 40 turns of work (O S15). Printing Press, the Free Speech and Universal Suffrage civics and golden ages add yield to grown towns, and Emancipation doubles their growth rate (O S15). Roads cut a move to half a movement point, a third after Engineering, and railroads to a tenth; railroads need coal or oil and add a hammer to mines, lumbermills and quarries, while roads give no speed in enemy land without the Commando promotion (O S14, S16). Forts add a defence bonus that siege cannot bombard away (O S40), and chopping a forest gives a one-off burst of hammers (O S13). The choice between cottage, farm and mine decides whether a city is a commerce, food or production city, and a mature town is worth defending (I).

**Rating: MUST** for farms, mines, workshops, roads, railroads and the cottage chain; **LATER** for watermills, windmills, lumbermills and forts. A Freeciv extra can appear by itself each turn with a set chance once its requirements hold (O S92), and "worked by a city" is a valid tile requirement (O S86), so a hamlet could appear on a worked cottage at about 10% a turn, which gives random rather than fixed timing (I).

### 2.4 City management

#### Growth and food

Each citizen eats 2 food, the surplus fills a food box, and a full box adds one citizen (O S17). The box grows linearly, about 22 food at size 1 plus 2 for each further size, and slower game speeds scale it up (O S17, S18). A granary keeps half the box after growth, a city grows at most one size per turn, and whipping leaves the box untouched (O S17, S18). Specialists eat like everyone else but produce no food (O S17). Linear growth keeps mid-size cities growing steadily, so the binding limits are happiness and health rather than the box (I).

**Rating: MUST.** Freeciv sets food per citizen in the ruleset (civ2civ3 uses 2), builds the box from a list of sizes plus a step, and has a Growth_Food effect that keeps part of the box (O S86, S88), so this is ruleset-only work (D).

#### Health and happiness caps

Each city has a content limit set mainly by difficulty, from about 6 at the easiest levels to 3 at the hardest, and citizens above it are unhappy (O S19). Unhappiness comes from city size, a missing garrison in cities of size 3 or more, recent whips (one face each for 10 turns) and drafts (three faces), war weariness and the foreign culture of captured cities (O S19). Happiness comes from luxury resources, temples and other buildings, the state religion, wonders, civics and the culture slider (O S19). Citizens beyond the cap refuse to work but still eat, and cities do not riot from unhappiness (O S7, S19). Health works the same way: population, flood plains, jungle and industrial buildings add unhealthiness, while fresh water, nearby forest, food resources, some buildings and the Expansive trait add health, and each point of excess costs a food per turn (O S20). Together these caps replace Civ2's riots and pollution clean-up (O S7), so growth is limited by trade, religion and buildings rather than by micromanaged entertainers (I).

**Rating: MUST, approximated.** Freeciv has content effects, an empire-size unhappiness penalty and a plague model that Health_Pct reduces (O S86, S88), but its unhappy cities fall into disorder instead of idling citizens (I). A first version can tune Freeciv's caps to Civ4's values and model unhealth as food waste or a size limit through Output_Waste or Size_Adj (I; the effects exist, O S86).

#### Production, whipping and drafting

Hammers from worked tiles fill the current build, and the excess carries over to the next one (O S9, S21). Under the Slavery civic a player can whip a city, sacrificing citizens to finish the build at once: about 30 hammers per citizen, fewer if nothing has been invested yet, a worse rate for wonders, and at most half the population (O S21). Each whip adds one unhappy face for 10 turns, and repeated whips stack (O S21). Under the Nationhood civic a player can draft a unit instantly for 1 to 3 citizens, with an empire-wide limit of 1 to 5 drafts a turn depending on map size, three unhappy faces for 10 turns, and a rule that the city keep at least 5 citizens and some of the player's culture (O S22). Universal Suffrage lets gold buy builds, and chopping forest gives one-off hammers (O S56, S13). Whipping turns food into hammers, so a fast-growing city on Slavery works like a production city, which makes it the signature early-game tactic (I, from S21, S24).

**Rating: MUST** for hammers, overflow, gold buying and chopping; **LATER** for whipping and drafting. Freeciv already keeps surplus shields after a build (O S98), but its Lua API has no call to shrink a city or add shields (D from S93, S94, by search). Whipping needs a small engine change or a workaround such as a cheap levy unit with a population cost, whose shield value is raised by Unit_Shield_Value_Pct and then recycled into the build with "Disband Unit Recover" (I; the pieces exist, O S85, S86, S87).

#### Commerce sliders

Commerce from tiles and trade routes is split by sliders, in 10% steps, between science, gold and culture, and BTS adds a fourth share for espionage (O S23, S3). Buildings such as libraries and markets then multiply each share (O S23). City and unit maintenance and civic upkeep come out of the gold share, and players often run science at a deficit while a gold reserve lasts (O S23, S28, S57). The culture slider also produces happiness, which makes it a late-game emergency lever (O S19; I). The espionage slider appears after meeting another civ (O S31). A tech costs less when civs you have met already know it, so trailing civs catch up (O S30). Tying the whole economy to commerce is why cottages, rivers and trade matter so much (I).

**Rating: MUST** for science, gold and culture shares; **LATER** for espionage. Freeciv already has tax, luxury and science rates with a per-government maximum (Max_Rates) and a tech-leakage catch-up (O S86, S88), so the luxury rate can stand in for the culture slider's happiness at first, with culture added by Lua through add_city_history (I; O S93).

#### Specialists

Citizens not working tiles become specialists; BTS has seven kinds, a plain citizen plus priest, artist, scientist, merchant, engineer and spy (O S25). Each named specialist gives a few points of output, about 2 to 5 in total and led by its signature yield, plus 3 Great Person points toward its type, while the plain citizen gives one hammer and no points (O S25; the range is D). Most slots come from buildings, and some civics lift the limits or add to every specialist (O S24, S25). A settled Great Person becomes a permanent super-specialist (O S25, S50). Specialists anchor one of the three recognised economies: cottage, specialist, or a hybrid of the two (O S24).

**Rating: MUST.** Freeciv rulesets define their own specialists with outputs set by the Specialist_Output effect (O S86), and civ2civ3 has three (O S91), so civ45 can define Civ4's seven (I). Great Person points from specialists are harder: Lua can read effect totals but I found no specialist count in its API (D from S94, by search).

#### Trade routes

Trade routes are automatic: each city has a number of route slots and the game picks the partners, with no caravans involved (O S26). Extra slots come from a few techs, the Free Market civic, airports, the Great Lighthouse and a UN resolution (O S26). A route needs a road, river or coastal link, or open ocean after Astronomy; foreign routes need Open Borders, and the Mercantilism civic blocks them (O S26). Yield rises with distance and partner size, overseas and foreign routes pay more, and harbours and customs houses add to them (O S27). Trade is quiet background income that rewards peace, Open Borders and coastal cities (I).

**Rating: LATER.** Freeciv routes are made by caravan-type units through the Establish Trade Route and Enter Marketplace actions and capped by Max_Trade_Routes (O S85, S86), and its Lua API has no call to create a route (D from S93, by search); a flat commerce bonus per city can stand in at first (I).

### 2.5 Combat

#### Strength, hit points, odds and rounds

Every unit has one strength value used for both attack and defence (O S7, S32). Situational bonuses are percentages, and the attacker's bonuses are applied as penalties to the defender, so everything nets into two final numbers (O S32). Units have 100 hit points; each round the attacker wins with a chance equal to its share of the combined strength, and the loser of the round takes damage that grows with the strength ratio, about 20 at even strength and kept within roughly 6 to 60 (O S32, S33). Damage lowers effective strength, so wounded units fight worse, and combat runs until one side dies or withdraws (O S32, S33). Because the ratio drives both the odds and the damage, small strength edges compound into large win chances (D from S32, S33).

**Rating: MUST** for one strength per unit and percentage modifiers; **LATER** for ratio-based damage. Freeciv already decides each round with the same strength-share chance, but the loser of a round always loses a fixed firepower amount (O S83). Setting attack equal to defence and using Attack_Bonus, Defend_Bonus and per-unit combat bonuses gets close (I; the effects and bonuses exist, O S86, S87), while ratio damage sits in the C combat loop (D from S83).

#### First strikes and withdrawal

Some units and promotions grant first strikes, free opening rounds in which only that side can hit, and when both sides have them only the difference counts (O S32, S44). First strikes are ignored when the game picks a stack's defender (O S36). Units with a withdrawal chance, mostly mounted ones, may retreat damaged when the losing blow comes instead of dying (O S32; "mostly mounted" is I). In BTS siege units cannot kill: once the defender is down to the siege unit's damage limit, the siege unit withdraws (O S5, S36). These rules give each unit class a combat character beyond its strength number (I).

**Rating: LATER.** Freeciv's combat loop has no first-strike rounds and no withdrawal chance (D from S83), and its CanEscape flag is a different rule that only lets units on a losing tile flee when killstack is on (O S87). A Combat_Rounds cap, which ends a fight after a set number of rounds, could approximate the BTS siege damage limit (I; the effect exists, O S86).

#### Terrain, river, fortify and city defence

Defenders gain from terrain (forest or jungle about 50%, hills 25%, both 75%) and from an attacker crossing a river (O S14). Fortifying adds a bonus that builds over a few turns, about 25% at most by one player's account (O S41; uncertain). A city adds the higher of its culture defence, 20% per culture level up to 100%, or its walls at 50% (O S38). Siege units, some ships and aircraft bombard that city bonus down each turn, walls and castles slow the bombardment, and gunpowder units ignore walls and castles altogether (O S39, S40). A fort gives a bonus that cannot be bombarded away (O S40).

**Rating: MUST.** Freeciv terrains and the river extra carry their own defence bonuses (O S92), and Defend_Bonus applies its unit requirements to the attacker, so walls that do not count against gunpowder attackers are plain ruleset data (D from S86). Fortify_Defense_Bonus covers fortifying, and a set of MinCulture thresholds can step city defence up with culture (I; the effect and requirement exist, O S86).

#### City attack bonuses

The City Raider promotion line, starting at 20% for its first level, is the main tool for taking cities (O S32, S44). Many units also carry built-in bonuses against a class of units, the source of Civ4's counter system (O S49). The usual siege is to bombard the defences to zero, soften the stack with collateral damage, then attack with City Raider units (I, from S32, S35, S39).

**Rating: MUST.** Freeciv unit types already take combat bonuses against other units' flags and flags such as CityBuster for attacking cities (O S87), so class counters and City Raider-style bonuses are mostly ruleset data (I).

### 2.6 Stacks

Any number of units can share a tile and move together, but each attack is a duel between one attacker and one defender (O S1, S34). The defender is the unit with the best odds against that particular attacker, not simply the strongest (O S35, S42), and only the loser dies; the rest of the stack is untouched apart from collateral damage and flanking (O S34). Siege units (catapult, then cannon, then artillery) also damage several other units in the target stack, and both the number hit and the damage cap rise each era, from about half health on 5 units to about 70% on 7 (D from S32). Collateral damage never kills, and a unit that is defending deals none (O S35, S36). Fast mounted units flank: if they survive an attack, by winning or withdrawing, they also damage siege units in the defending stack (O S37). The result is the Civ4 "stack of doom", a mix of defenders, siege and attackers, often dozens of units strong in AI hands (O S6, S35). The answer to a big stack is your own siege and a strong defensive position, so wars turn on army composition, not only size (I).

**Rating: MUST** for stacking where only the loser dies, the best-defender rule and siege collateral; **LATER** for flanking. Freeciv's killstack setting is on by default, can be switched off so only the defender dies, and can be preset by a ruleset (O S80, S81, S88). Its defender choice already picks the unit with the best odds against that attacker (O S82). Its Bombard action damages every unit on a tile and can be made non-lethal (O S83, S84, S85). For Civ4's exact caps and for flanking, Lua can run after an attack and remove hit points from chosen units (O S93, S95, S96; that this is enough is I).

### 2.7 Experience

Units earn XP from battle, about 4 times the strength ratio for a won attack and 2 times for a won defence, at least 1 point, capped at 10 XP from barbarians and 5 from animals (O S32, S43). Barracks, some civics, wonders and Great Generals give new units starting XP (O S44, S45). Each level costs more XP, the square of the level plus one (2, 5, 10, 17 and on), and the Charismatic trait cuts that by a quarter (O S43). At each level the player picks a promotion from branching lines: Combat (general strength), City Raider (city attack), City Garrison (city defence), Drill (first strikes), Shock, Cover and Formation (bonus against one class), Medic (healing), Barrage and Accuracy (siege), Flanking (withdrawal), and terrain lines such as Guerrilla and Woodsman (O S44); a melee unit might take Combat I, then Shock, then Combat II, and a catapult Barrage for more collateral (I, from S44). Great Generals come from combat against non-barbarians, each one needing more points (O S45). A general can join a city as an instructor that gives its new units 2 XP, build a Military Academy, or attach to a unit as a Warlord, which spreads 20 XP across its stack and unlocks leader-only promotions such as Leadership and Tactics (O S2, S45). Upgrading keeps promotions, but sources report that stored XP drops to 10 unless the unit is a Warlord (O S43, S45).

**Rating: MUST** for XP and a promotion ladder; **LATER** for branching choices and Great Generals. Freeciv's veteran system is one linear ladder per ruleset with chance-based level-ups; civ2civ3 has four levels, green to elite, at 100 to 200% power (O S87). The project notes class branching promotions as engine work, with a Lua stopgap that transforms a unit into a pre-made variant type (O S100; Unit:transform exists, O S93). Great Generals are a Lua job: count combat results and create a general unit (I; create_unit exists, O S93).

### 2.8 Unit roster shape

BTS has about 85 standard units, plus 34 unique replacements and 4 animals (O S46). Spread over seven eras that is roughly a dozen new units per era, and strength climbs from about 1 to 6 in the ancient era to about 24 to 40 in the modern era, roughly 1.5 to 2 times per era (D from S46). The classes are melee, archery, mounted, gunpowder, siege, armoured, helicopter, naval, air, missile and recon (O S46). Built-in bonuses form a rock-paper-scissors web, for example spear-type units against mounted ones (O S49). Units upgrade to their successors for gold, and the AI pays less for upgrades (O S6, S43). Early melee units need copper or iron, mounted units horses (elephants ivory), gunpowder infantry nothing, ironclads iron and coal, later ships oil or uranium, tanks and aircraft oil, some late units aluminium, and nuclear weapons uranium plus the Manhattan Project (O S46). Each civ gets one unique unit that replaces a standard one with a modest edge, and one unique building (O S47, S48, S2). Losing a resource can halt a whole unit line, so resources become military targets (I).

**Rating: MUST.** Breadth and counters are what make the war game Civ4-like (I). Freeciv unit types carry classes, per-flag combat bonuses, upgrade paths and requirements, and a Nation requirement can limit a unique unit to one nation (O S86, S87); resource gating depends on the network emulation in 2.2 (I).

### 2.9 Great People and golden ages

BTS has seven kinds of Great Person: prophet, artist, scientist, merchant, engineer, general and spy (O S50, S25). Each specialist adds 3 points a turn to its city's pool, and world and national wonders add 2 and 1 (O S50). When a city's pool reaches the current threshold a Great Person is born there, its type drawn at random in proportion to each type's share of the points (O S50). The threshold starts at 100 and rises by 100 per birth up to 1,000, then by 200, scaled by game speed, and the Philosophical trait, the Pacifism civic and some wonders speed births (O S50, S51). The first civ to certain techs gets a free Great Person (O S50). A Great Person can settle as a super-specialist or be spent once: a prophet builds a shrine, an artist adds a burst of culture, a scientist discovers a tech, a merchant runs a trade mission for gold, an engineer hurries production, and any of them can help start a golden age (O S50). In BTS the first golden age takes one Great Person, the next two of different types, then three, and the Taj Mahal grants one; each lasts 8 turns, adds a hammer and a commerce to tiles already producing them, doubles Great Person points and removes anarchy (O S52). This stream of Great People sets the pace of specialist and wonder strategies (I).

**Rating: MUST, simplified.** The project notes place Great People in the Lua tier (O S100). Lua can create a Great Person unit, give research bulbs, add culture and gold, and read per-city effect totals, so the ruleset can define points from buildings and wonders through the blank User_Effect slots; Help Wonder already lets a unit pour its shields into a wonder (O S85, S86, S93, S94). A golden age can be a temporary national building that Lua adds and removes (I).

### 2.10 Religion

BTS has seven religions that work identically; only names and art differ (O S53, S1). Each is founded by the first civ to discover its tech, in one of that civ's cities, which becomes the holy city (O S53). Religions spread on their own only into cities with no religion yet, along trade connections, with distance affecting the odds (O S53). Missionaries spread them on purpose, and each attempt fails more often the more religions the city already has, about 9% per religion at home and 12% abroad (O S53). Each faith has its own temple, monastery and cathedral, which add happiness, culture and other bonuses, and a Great Prophet can build a shrine in the holy city that earns gold from every city of that faith worldwide (O S50, S53). A state religion adds happiness, and AI leaders like civs that share their state religion and dislike those that do not (O S53, S67). The Apostolic Palace lets members of its religion vote on resolutions, including a diplomatic victory at 75%, until Mass Media makes it obsolete (O S54, S3). Religion is the main early force that sorts the AIs into friends and rivals (I).

**Rating: MUST, simplified.** Freeciv has no religion, and the project notes put a real religion system in the engine tier (O S100). A first version can use Lua and marker buildings: Lua founds a religion when its tech is first learned, spreads it to cities without one each turn, and the markers drive temple and state-religion happiness and shrine gold (I; the tech signal and building calls exist, O S93, S95). Missionaries, the Apostolic Palace and AI attitude effects come later (I).

### 2.11 Civics

Civics come in five categories (government, legal, labour, economy and religion) of five options each, and every civ starts on a free default in each (O S55). New options unlock with techs, and players combine one choice per category, for example Slavery for whipping beside Hereditary Rule, which offsets the whip's unhappiness (O S56, S21). Each civic has an upkeep level from none to high, the gold cost grows with the number of cities and population, and the Organized trait halves it (O S57). Switching causes a short period of anarchy, changing several civics at once is cheaper than changing them one by one, and Spiritual leaders switch without anarchy (O S56). Each AI leader has a favourite civic and likes civs that run it (O S67, S75). Civics turn Civ2's single government into a toolkit, and switching to wartime civics is a real strategic decision (I).

**Rating: MUST.** Freeciv governments can serve as the government column (civ2civ3 has nine) and the No_Anarchy effect covers Spiritual (O S86, S89). Freeciv's multipliers are sliders rather than exclusive choices (O S90), so the other four columns are better modelled as mutually exclusive national "policy" buildings that Lua swaps, with civic upkeep as their gold upkeep (I).

### 2.12 Leaders and traits

BTS has 52 leaders across 34 civilisations (D from S58, by counting; O S1 for 34 civs), and each leader has two of eleven traits (O S58). Each trait is a small always-on bonus, usually paired with faster building of one or two related buildings (O S59). Examples: Financial adds a commerce to tiles that already make 2, Philosophical doubles Great Person points, Spiritual removes anarchy, Organized halves civic upkeep, Aggressive gives melee and gunpowder units a free first promotion, and Charismatic adds happiness and cheapens promotions (O S59). Their value depends on synergy, for example Financial with cottages and Philosophical with specialists (O S59), and one analysis finds Philosophical yields about half again as many Great People over a game (O S60). Each civ also starts with two techs and has its own unique unit and building (O S9, S47, S48). Two traits per leader make the same civ play differently under different leaders (I).

**Rating: MUST.** Traits are cheap to express as effects with a Nation requirement (O S86), but there is no per-leader requirement that I know of, so civ45 should give each nation one trait pair (I).

### 2.13 Culture

Cities earn culture from buildings, wonders, religion, Great Artists, specialists and the culture slider, multiplied by some buildings and civics (O S61). A city's culture level rises at thresholds that grow roughly tenfold, from 10 points for the second level to 50,000 for the sixth and top level, Legendary (O S61). Each level widens the city's cultural reach by one ring of tiles, and a tile belongs to the civ with the most culture on it among cities in range (O S61). A city with more foreign culture than its owner's on its own tile can revolt, with occasional checks that compare a revolt score against the garrison's strength, and revolts can end with the city flipping to the other civ (O S61). Culture also raises city defence by 20% per level up to 100% (O S38), and three Legendary cities win a culture victory (O S61, S72). Culture lets a peaceful builder take land and even cities without war (I).

**Rating: MUST** for culture points, levels, borders, city defence and culture victory; **LATER** for revolts and flipping. Freeciv 3.2 tracks per-city and national culture through the History and Performance effects, has a MinCulture requirement and a culture victory, and Lua can add culture with add_city_history (O S80, S86, S93). The project notes report culture-driven borders already working in civ45 (O S100, S101); for a Civ4 feel, borders should follow culture while the work radius stays fixed (D from S11, S61). Flipping can use Lua's transfer_city (I; the call exists, O S93).

### 2.14 Wonders

BTS has about 34 world wonders, one per world, and about 14 national wonders, one per civ, plus shrines, corporation headquarters and projects such as the Manhattan Project and the Apollo Program (D from S62, by counting; O S62). A city may hold at most two national wonders (O S63). Stone and marble roughly halve the build time of the wonders they apply to, and the Industrious trait adds 50% (O S79, S59). When a rival finishes a wonder first, the hammers you invested turn into gold (O S79). Wonders give unique effects, Great Person points, culture and sometimes a golden age (O S50, S52, S62). No one can build them all, so choosing and racing for wonders is a constant thread (O S9; I).

**Rating: MUST.** Freeciv buildings already come in great-wonder and small-wonder genera (O S99), and caravan-style units can add their shields to a wonder through Help Wonder (O S85). Resource-based wonder bonuses can use Output_Bonus with a city-range Extra requirement (I; O S86).

### 2.15 Later systems

**Corporations.** BTS has seven corporations, each founded by a Great Person of the right type once a tech is known (O S64). The founding city becomes the headquarters, and executive units, which cost gold to use, open branches in other cities (O S64). A branch consumes certain resources and produces output such as food, hammers, culture or new resources, scaled by the number of resources consumed and by map size (O S64). The headquarters earns gold from every branch, branches add maintenance, competing corporations exclude each other, and some economic civics block or disable them (O S64, S65). They turn late-game resources into a second economy (I).

**Rating: SKIP** for the first playable; **LATER** once the religion emulation works, since branches spread much like religions (I).

**Espionage points and missions.** BTS adds espionage points, produced by the slider, buildings and spy specialists, which build up separately against each known rival (O S3, S31). Passing point thresholds against a rival reveals its demographics, research and cities and lets you investigate them (O S3, S31). Spies, available from Alphabet, are invisible to other civs and spend points on missions such as stealing a tech, sabotage, poisoning water, inciting revolt or forcing a civic or religion change (O S3, S31, S66). Mission cost depends on distance, the two sides' point balance, culture, religion and how long the spy has waited in place (O S66). A caught spy brings a hidden diplomatic penalty (O S3). Espionage gives non-military players a way to hurt rivals (I).

**Rating: LATER.** Freeciv's diplomat and spy units already perform action-based missions such as stealing tech, sabotage and inciting revolt (O S85), which can stand in until points exist (I).

### 2.16 Diplomacy

Players trade techs, gold, resources, cities, maps and agreements such as Open Borders (from Writing) and Defensive Pacts (from Military Tradition), while Permanent Alliances are off by default (O S67). Each AI's attitude toward you is a visible sum of modifiers, plus for a shared religion, running its favourite civic, Open Borders and trade, minus for a different religion, wars, refused demands and crowded borders (O S67, S68), and many of these come from remembered events (D from S67). Attitude bands from Furious to Friendly gate what the AI will trade, Pleased begins at about +3, and no leader attacks a civ it is Friendly with (O S68). A Defensive Pact pulls both members into a war when either is attacked and is cancelled if a member starts one (O S67, S71). In BTS a beaten civ can capitulate and a weak one can volunteer as a vassal; the master protects it and counts half its land and population toward domination, and the vassal can break free when the balance shifts (O S69). BTS also lets a player split off distant cities as a colony (O S3). The Apostolic Palace and later the UN hold elections on resolutions, with UN votes weighted by population (O S54, S70). Visible attitudes make diplomacy feel fair, because players can see why a leader likes them and act on it (I).

**Rating: MUST** using Freeciv's native diplomacy as it is; **LATER** for vassals, the Apostolic Palace and UN votes. Freeciv's AI keeps a "love" level toward each player that rulesets can nudge with Gain_AI_Love (O S86), and Lua's player_victory could award a scripted diplomatic win later (I; the call exists, O S93).

### 2.17 Victory conditions

BTS offers six victories: conquest, domination, culture, space race, diplomatic and time (O S72). Conquest means eliminating every rival, and in BTS a rival that capitulates as a vassal counts as conquered (O S72). Domination needs a large share of the world's land, about 65%, plus a population lead, and the thresholds vary from game to game (O S72). Culture needs three Legendary cities (O S72), the space race needs a spaceship that in BTS must also complete its flight (O S3), and diplomacy needs about 60% of the vote in a UN leader election or 75% in the Apostolic Palace (O S72, S54). If no one wins, the highest score takes a time victory at the end date, 2050 AD at normal speed (O S72). Several routes let builders and warmongers both chase a win (I).

**Rating: MUST** for conquest, culture, space race and score; **LATER** for domination and diplomatic. Freeciv's victories setting already covers space race, allied and culture wins, and an end-turn setting closes the game (O S80); Lua's player_victory can award a scripted domination win (I; the call exists, O S93).

### 2.18 Other

**Barbarians.** Animals roam unclaimed land early, barbarian warriors and archers follow, and later barbarian cities appear on unsettled land (O S74). Barbarians only spawn on tiles no player can see, so scouting and settling push them back (O S73). The Great Wall keeps them out of its owner's borders on that continent, and a Raging Barbarians option makes them far more numerous (O S73, S74). They give early defence a purpose and a capped source of XP (O S43; I).

**Rating: MUST** (native). Freeciv ships barbarian, pirate and animal nations, and Lua can trigger raids with unleash_barbarians (O S93, S97).

**Random events.** BTS adds a large set of random events and quests, over 100 by one count and about 150 by another (O S3, S4). Events fire only when the game state fits, such as owning a resource or building, and many offer a choice between costs and rewards (O S4). Quests set a goal with a deadline and a reward (O S4). They add story and small swings rather than core strategy (I).

**Rating: LATER.** Freeciv rulesets already define disasters with requirements and effects, and civ2civ3 has five (O S88); Lua can script more (I).

**AI personality model.** Each leader has a personality: a favourite civic, willingness to trade techs, how much it builds wonders, units and spies, how often it demands tribute, how likely it is to start wars, how much it values peace, its base attitude, and whether it can plan a war while Pleased (O S75). Players share lore about individual leaders, such as which forgive easily and which attack while still Pleased (O S76). Visible attitude, and certain refusals in trade talks, let players read a leader's war plans (O S68). Distinct but predictable leaders are a large part of Civ4's diplomatic feel (I).

**Rating: LATER.** Freeciv gives each nation AI traits for expansion, trade, aggression and building, drawn from a range, and Lua can adjust them during play (O S93, S97); mapping each Civ4 personality onto these four traits is a cheap first step (I).

## 3. Recommendation: the first playable civ45

These MUST systems together reproduce the decisions a Civ4 player makes every turn, which is most of the feel (I):

1. **Board:** square topology, a fixed 21-tile fat cross (squared radius 5), stock map sizes, and culture-driven borders (D from S80, S88, S100).
2. **War:** killstack off, one strength per unit (attack equals defence), Civ4-style percentage bonuses for terrain, fortification, city culture and walls, class counters and city attack, non-lethal siege collateral, and a linear promotion ladder (I; mechanisms O S80 to S87).
3. **Roster:** about 85 units across seven eras with Civ4's classes and counters, resource gating through a Lua-kept national resource marker, and one unique unit and building per nation (I).
4. **Economy:** farms, mines, workshops, roads, railroads and the cottage chain; a linear food box; content and health caps tuned to Civ4; gold upkeep paid nationally for buildings and units (gold_upkeep_style "Nation") plus distance-based gold waste in place of city maintenance; seven specialists; science, gold and luxury rates (I; O S86, S88).
5. **Civics:** Freeciv governments as the government column, the other four columns as mutually exclusive policy buildings swapped by Lua, and No_Anarchy for Spiritual leaders (I; O S86).
6. **People and culture:** Lua Great People with their one-off uses and golden ages; culture points, levels, city defence and culture victory (I; O S86, S93).
7. **Religion, simplified:** seven Lua-founded religions as city marker buildings with passive spread, temples, state-religion happiness and shrine gold (I).
8. **Kept native:** Freeciv diplomacy, barbarians and animals, and space, culture and score victories (O S80, S97).

Why this scope (I): it covers the core loop of settling inside a fat cross, choosing cottage, farm or mine, growing to the caps, stacking a mixed army, picking civics, racing for wonders and harvesting Great People. It needs only ruleset data and Lua, which keeps civ45 runnable on a stock Freeciv server as the project notes want (O S101). Stacks also suit Freeciv's default AI, which the notes say assumes stacking (O S100).

**Defer, in roughly this order (I):** Great Generals and flanking (Lua); whipping and drafting; branching promotions; first strikes, withdrawal and ratio damage (engine); trade-route automation; espionage points; corporations; vassals, the Apostolic Palace and the UN; random events; AI personality mapping.

## 4. Open questions

1. **Which game is civ45?** This brief describes civ45 as Civ4-like (square tiles, stacks), but the project notes record John's 2026-10-16 goal of making civ45 feel more like Civ5, and civ45 slices 1 and 2 already ship hex topology and one unit per tile (patches 0003 and 0004) (O S100, S101). Does the hex and one-unit-per-tile work move to civ54 while civ45 restarts from square tiles and stacks?
2. **Resource network:** is a Lua-granted national marker per resource acceptable, or should Extra requirements gain player range in the engine (O S86; I)?
3. **Civics:** policy buildings, multipliers (which are sliders, O S90) or an engine feature?
4. **Whipping:** prototype the levy-unit workaround, or add a Lua call that shrinks a city, a small engine change (I)?
5. **Combat feel:** is Freeciv's fixed damage per round close enough once attack equals defence and hit points are tuned, or is ratio-based damage worth an engine patch? Autogame comparisons can decide (I).
6. **Promotions:** pre-made variant unit types through Unit:transform (Lua tier) or a real promotion system (engine tier) (O S93, S100)?
7. **Uncertain Civ4 numbers:** the fortify bonus (S41 is one player's memory), domination thresholds (S72 says they vary), XP kept on upgrade (S43 reports disagreement), draft limits (S22), and food box and whip values at other game speeds (S17, S18, S21) need more sources (I).
8. **Health:** a hard size cap (Size_Adj) or Civ4's food penalty (food Output_Waste) (I; O S86)?
9. **Unhappiness:** keep Freeciv's civil disorder or emulate Civ4's idle unhappy citizens, which likely needs engine work (I)?
10. **AI:** the default AI will not understand Lua-only systems such as religion spread, Great People or policy buildings; how much AI support does the first playable need (I)?

## 5. Sources

Secondary sources on Civ4 and Civ2 (all public; Fandom pages read in a browser with Civilopedia, quote and history sections skipped):

- S1 Wikipedia, Civilization IV: https://en.wikipedia.org/wiki/Civilization_IV
- S2 Wikipedia, Civilization IV: Warlords: https://en.wikipedia.org/wiki/Civilization_IV:_Warlords
- S3 Wikipedia, Civilization IV: Beyond the Sword: https://en.wikipedia.org/wiki/Civilization_IV:_Beyond_the_Sword
- S4 Apolyton, BTS review by Solver, page 6: https://apolyton.net/articles/civilization-news/civ4/p-reviews-ac/9313017-civilization-iv-beyond-the-sword-review-by-solver/contentpage6
- S5 Same review, page 7: https://apolyton.net/articles/civilization-news/civ4/p-reviews-ac/9313017-civilization-iv-beyond-the-sword-review-by-solver/contentpage7
- S6 Same review, page 8: https://apolyton.net/articles/civilization-news/civ4/p-reviews-ac/9313017-civilization-iv-beyond-the-sword-review-by-solver/contentpage8
- S7 Apolyton, Civ4 review by Yin26, part 2: https://apolyton.net/articles/civilization-news/civ4/p-reviews-ac/9313012-civilization-4-review-by-yin26-part-2-3
- S8 CivFanatics forum, Transitioning to IV: https://forums.civfanatics.com/threads/transitioning-to-iv.262349/
- S9 CivFanatics, Tips for people who hate Civ4: https://civfanatics.com/civ4/strategy/introductory/tips-for-people-who-hate-civ4/
- S10 CivFanatics forum, Hex vs squares: https://forums.civfanatics.com/threads/hex-vs-squares.371822
- S11 CivFanatics forum, Quick Answers p. 449: https://forums.civfanatics.com/threads/quick-answers-newbie-questions.134903/page-449
- S12 Apolyton forum, Civ3 vs Civ4 world size: https://apolyton.net/forum/civilization-iv/civilization-iv-general/157486-civ3-vs-civ4-world-size-how-different
- S13 CivFanatics, Guide to terrain, improvements, resources and city placement: https://civfanatics.com/civ4/strategy/empire-management/comprehensive-guide-to-terrain-improvements-resources-and-city-placement/
- S14 CivFanatics forum, A guide to terrain and improvements: https://forums.civfanatics.com/threads/a-guide-to-terrain-and-improvements.136433
- S15 CivFanatics forum, Cottages: https://forums.civfanatics.com/threads/cottages.301724/
- S16 Civilization Wiki (Fandom), Road and railroad (Civ4): https://civilization.fandom.com/wiki/Road_and_railroad_(Civ4)
- S17 CivFanatics, City growth: https://civfanatics.com/civ4/strategy/game-mechanics/city-growth/
- S18 CivFanatics, Inner mechanics of food, growth, granary and whipping: https://civfanatics.com/civ4/strategy/game-mechanics/the-inner-mechanics-of-food-growth-granary-and-whipping/
- S19 CivFanatics, Ways into happiness: https://civfanatics.com/civ4/strategy/empire-management/ways-into-happiness/
- S20 CivFanatics, Ways into health: https://civfanatics.com/civ4/strategy/empire-management/ways-into-health/
- S21 CivFanatics, Vocum sineratio: the whip: https://civfanatics.com/civ4/strategy/empire-management/vocum-sineratio-the-whip/
- S22 CivFanatics, Drafting for fun and profit: https://civfanatics.com/civ4/strategy/military/drafting-for-fun-and-profit/
- S23 CivFanatics, Gold, beakers and deficit research: https://civfanatics.com/civ4/strategy/empire-management/gold-beakers-and-deficit-research/
- S24 CivFanatics, The types of economies: https://civfanatics.com/civ4/strategy/empire-management/the-types-of-economies/
- S25 Civilization Wiki (Fandom), Specialists (Civ4): https://civilization.fandom.com/wiki/Specialists_(Civ4)
- S26 Apolyton forum, Trade routes 101: https://apolyton.net/forum/civilization-iv/civilization-iv-general/208211-trade-routes-101
- S27 CivFanatics, Trade routes: https://civfanatics.com/civ4/strategy/game-mechanics/trade-routes/
- S28 CivFanatics, City upkeep explained: https://civfanatics.com/civ4/strategy/game-mechanics/the-curious-cat-city-upkeep-explained/
- S29 CivFanatics, Unit maintenance explained: https://civfanatics.com/civ4/strategy/game-mechanics/unit-maintenance-explained/
- S30 CivFanatics, Technology research explained: https://civfanatics.com/civ4/strategy/game-mechanics/technology-research-explained/
- S31 CivFanatics forum, Complete guide to espionage: https://forums.civfanatics.com/threads/the-complete-guide-to-espionage.638613/
- S32 CivFanatics, Combat explained: https://civfanatics.com/civ4/strategy/game-mechanics/combat-explained/
- S33 CivFanatics, How simple combat works (1.61): https://civfanatics.com/civ4/strategy/game-mechanics/how-simple-combat-works-in-1-61-vanilla/
- S34 CivFanatics forum, Quick Answers p. 341: https://forums.civfanatics.com/threads/quick-answers-newbie-questions.134903/page-341
- S35 CivFanatics forum, Stacking from 1UPT tips: https://forums.civfanatics.com/threads/stacking-from-1upt-tips.467199
- S36 CivFanatics forum, Help with stacks of doom: https://forums.civfanatics.com/threads/help-with-stacks-of-doom.571129
- S37 CivFanatics forum, Flank attacks: https://forums.civfanatics.com/threads/flank-attacks-how-to.243066/
- S38 CivFanatics forum, How does culture defense work: https://forums.civfanatics.com/threads/how-does-culture-defense-work.170230/
- S39 CivFanatics forum, How does bombardment work: https://forums.civfanatics.com/threads/how-does-bombardment-work.354773/
- S40 CivFanatics forum, Obsolescence and city defense, p. 2: https://forums.civfanatics.com/threads/obsolescence-and-city-defense.340142/page-2
- S41 CivFanatics forum, Fortified units: https://forums.civfanatics.com/threads/fortified-units-implementation-and-value.540476
- S42 CivFanatics forum, The best defender rule in BTS: https://forums.civfanatics.com/threads/the-best-defender-rule-in-bts.244148
- S43 CivFanatics forum, Experience points and leveling: https://forums.civfanatics.com/threads/experience-points-and-leveling.247227
- S44 CivFanatics forum, Unit promotions strategy guide: https://forums.civfanatics.com/threads/unit-promotions-strategy-guide.240978
- S45 CivFanatics forum, Using the Great General: https://forums.civfanatics.com/threads/using-the-great-general.307864/
- S46 Civilization Wiki (Fandom), List of units in Civ4: https://civilization.fandom.com/wiki/List_of_units_in_Civ4
- S47 CivFanatics, Unique unit guide: https://civfanatics.com/civ4/strategy/military/a-comprehensive-unique-unit-guide/
- S48 CivFanatics, Unique building guide (BTS): https://civfanatics.com/civ4/strategy/empire-management/comprehensive-unique-building-guide-bts/
- S49 CivFanatics, Guide to using military units: https://civfanatics.com/civ4/strategy/military/guide-to-using-military-units/
- S50 Civilization Wiki (Fandom), Great Person (Civ4): https://civilization.fandom.com/wiki/Great_Person_(Civ4)
- S51 CivFanatics, Great People points explained: https://civfanatics.com/civ4/strategy/game-mechanics/great-people-points-explained/
- S52 Civilization Wiki (Fandom), Golden Age (Civ4): https://civilization.fandom.com/wiki/Golden_Age_(Civ4)
- S53 Civilization Wiki (Fandom), Religion (Civ4): https://civilization.fandom.com/wiki/Religion_(Civ4)
- S54 CivFanatics, Apostolic Palace guide: https://civfanatics.com/civ4/strategy/game-mechanics/the-apostolic-palace-guide/
- S55 Civilization Wiki (Fandom), List of civics in Civ4: https://civilization.fandom.com/wiki/List_of_civics_in_Civ4
- S56 CivFanatics, A guide to civics: https://civfanatics.com/civ4/strategy/introductory/a-guide-to-civics/
- S57 CivFanatics, Civic upkeep explained: https://civfanatics.com/civ4/strategy/game-mechanics/civic-upkeep-explained/
- S58 Civilization Wiki (Fandom), Leader trait (Civ4): https://civilization.fandom.com/wiki/Leader_trait_(Civ4)
- S59 CivFanatics, Traits, Warlords and synergy: https://civfanatics.com/civ4/strategy/introductory/traits-warlords-and-synergy/
- S60 CivFanatics, Analysis of the civilization traits: https://civfanatics.com/civ4/strategy/introductory/analysis-of-the-civilization-traits/
- S61 CivFanatics, Culture mechanics disassembled: https://civfanatics.com/civ4/strategy/game-mechanics/culture-mechanics-disassembled/
- S62 Civilization Wiki (Fandom), List of wonders in Civ4: https://civilization.fandom.com/wiki/List_of_wonders_in_Civ4
- S63 CivFanatics forum, Quick Answers p. 1111: https://forums.civfanatics.com/threads/quick-answers-newbie-questions.134903/page-1111
- S64 Civilization Wiki (Fandom), Corporation (concept) (Civ4): https://civilization.fandom.com/wiki/Corporation_(concept)_(Civ4)
- S65 CivFanatics, Corporations: the power of sushi: https://civfanatics.com/civ4/strategy/game-mechanics/corporation-the-power-of-sushi-bts/
- S66 CivFanatics, Espionage mission cost guide (BTS): https://civfanatics.com/civ4/strategy/game-mechanics/complete-espionage-mission-cost-guide-bts/
- S67 StrategyWiki, Civilization IV/Diplomacy: https://strategywiki.org/wiki/Civilization_IV/Diplomacy
- S68 CivFanatics forum, How to read the AI: https://forums.civfanatics.com/threads/how-to-read-the-ai.571726/
- S69 CivFanatics, Explaining the vassal system: https://civfanatics.com/civ4/strategy/game-mechanics/explaining-the-vassal-system/
- S70 CivFanatics, Diplomatic victory notes and tips: https://civfanatics.com/civ4/strategy/peacemonger/diplomatic-victory-observations-notes-and-tips/
- S71 CivFanatics forum, Defensive pacts: https://forums.civfanatics.com/threads/defensive-pacts.262580
- S72 Civilization Wiki (Fandom), Victory (Civ4): https://civilization.fandom.com/wiki/Victory_(Civ4)
- S73 CivFanatics forum, Dealing with barbarians: https://forums.civfanatics.com/threads/dealing-with-barbarians.251236
- S74 CivFanatics forum, How does barbarian city spawning work: https://forums.civfanatics.com/threads/how-does-barbarian-city-spawning-work.265173
- S75 CivFanatics forum, Civ Illustrated 1: know your enemy: https://forums.civfanatics.com/threads/civ-illustrated-1-know-your-enemy.478563/
- S76 CivFanatics forum, AI personalities: https://forums.civfanatics.com/threads/ai-personalities.247510
- S77 CivFanatics, Complete Civilization II combat guide: https://civfanatics.com/?p=248
- S78 Wikipedia, Freeciv: https://en.wikipedia.org/wiki/Freeciv
- S79 CivFanatics forum, Stone and marble: https://forums.civfanatics.com/threads/stone-marble.414127

Freeciv 3.2 source (GPL; read from a local checkout of branch S3_2):

- S80 server/settings.c (killstack, topology, map size, victories, end turn): https://github.com/freeciv/freeciv/blob/S3_2/server/settings.c
- S81 common/game.h (killstack on by default): https://github.com/freeciv/freeciv/blob/S3_2/common/game.h
- S82 common/combat.c (defender selection): https://github.com/freeciv/freeciv/blob/S3_2/common/combat.c
- S83 server/unittools.c (combat rounds, non-lethal bombard): https://github.com/freeciv/freeciv/blob/S3_2/server/unittools.c
- S84 server/unithand.c (bombard hits every unit on the tile): https://github.com/freeciv/freeciv/blob/S3_2/server/unithand.c
- S85 doc/README.actions: https://github.com/freeciv/freeciv/blob/S3_2/doc/README.actions
- S86 doc/README.effects (effects and requirement ranges): https://github.com/freeciv/freeciv/blob/S3_2/doc/README.effects
- S87 data/civ2civ3/units.ruleset (veteran system, unit flags, pop_cost, bonuses): https://github.com/freeciv/freeciv/blob/S3_2/data/civ2civ3/units.ruleset
- S88 data/civ2civ3/game.ruleset (food, radius, borders, illness, upkeep, granary, disasters, tech leakage, preset settings): https://github.com/freeciv/freeciv/blob/S3_2/data/civ2civ3/game.ruleset
- S89 data/civ2civ3/governments.ruleset: https://github.com/freeciv/freeciv/blob/S3_2/data/civ2civ3/governments.ruleset
- S90 data/goldkeep/governments.ruleset (multipliers): https://github.com/freeciv/freeciv/blob/S3_2/data/goldkeep/governments.ruleset
- S91 data/civ2civ3/cities.ruleset (specialists): https://github.com/freeciv/freeciv/blob/S3_2/data/civ2civ3/cities.ruleset
- S92 data/sandbox/terrain.ruleset (extras that appear by chance): https://github.com/freeciv/freeciv/blob/S3_2/data/sandbox/terrain.ruleset
- S93 server/scripting/tolua_server.pkg (Lua edit API): https://github.com/freeciv/freeciv/blob/S3_2/server/scripting/tolua_server.pkg
- S94 common/scriptcore/tolua_game.pkg (Lua getters and effects module): https://github.com/freeciv/freeciv/blob/S3_2/common/scriptcore/tolua_game.pkg
- S95 server/scripting/script_server.c (Lua signals): https://github.com/freeciv/freeciv/blob/S3_2/server/scripting/script_server.c
- S96 server/scripting/api_server_edit.c (hit point edits can kill): https://github.com/freeciv/freeciv/blob/S3_2/server/scripting/api_server_edit.c
- S97 data/civ2civ3/nations.ruleset (AI traits, barbarian and animal nations): https://github.com/freeciv/freeciv/blob/S3_2/data/civ2civ3/nations.ruleset
- S98 server/cityturn.c (surplus shields carried over): https://github.com/freeciv/freeciv/blob/S3_2/server/cityturn.c
- S99 data/civ2civ3/buildings.ruleset (wonder genera): https://github.com/freeciv/freeciv/blob/S3_2/data/civ2civ3/buildings.ruleset

Project notes (public):

- S100 notes/civ45-planning.md: https://github.com/John-ODell/freeciv-macos27/blob/main/notes/civ45-planning.md
- S101 notes/game-directions.md: https://github.com/John-ODell/freeciv-macos27/blob/main/notes/game-directions.md

## 6. Slice 2, Combat: what was built and what was seen (2026-10-17, patch 0008)

Freeciv45's combat slice (plan roadmap row 2, PR for issue 75) in `data/civ45` of the fork, all ruleset, no Lua. Labels as
in the plan: observed, derived, inferred. Line numbers are the fork's at commit `6777c85` (upstream S3_2 `44e6898` plus
patches 0001 to 0008).

### What the ruleset says now

- **Siege collateral.** Catapult, Cannon, Artillery and Howitzer carry a new user flag `Collateral` (`units.ruleset:54`)
  and a `bombard_rate` of 5, 10, 14 and 20 (`:1614,1657,1696,1734`). Four enablers for Freeciv's "Bombard 2" action
  (`actions.ruleset:1279-1337`, shown to the player as "Bombard Stack", `:342`) copy the aircraft "Bombard" enablers with
  that flag and one more target requirement, `"MaxUnitsOnTile", "1", "Tile", FALSE`: the tile must hold two or more
  units. "Bombard 2" is non-lethal by definition (`doc/README.actions:785-792`): each unit on the tile is shot at
  `bombard_rate` times and loses 1 hit point per hit, and a unit that would reach 0 keeps 1
  (`server/unittools.c:381-392`). Every reachable unit on the tile is hit (`server/unithand.c:4545-4546`). Bombarding
  spends the unit's whole turn (`effects.ruleset:4980`, as for aircraft). Against a lone unit the enabler is off and the
  siege unit attacks as before; against a stack "Attack" stays legal too (`bombard_2_blocked_by` lists only "Capture
  Units", `actions.ruleset:46`), so a human can choose. The rates are first guesses: against the defence values of their
  own era they take roughly a third to a half of each unit's hit points on open ground (derived from the round odds
  `attack / (attack + defence)`; not tuned).
- **To the death.** `Combat_Rounds` is 0 (`effects.ruleset:549`): a fight runs until the attacker or the defender dies
  (`server/unittools.c:329-332`; sandbox stopped every fight after 15 rounds, which between two 20-hit-point units
  could never end in a death).
- **Break-off for fast units.** A new user flag `Withdraws` (`units.ruleset:55`) on Horsemen, Chariot, Elephants,
  Crusaders, Knights, Dragoons, Cavalry and Armor. Three effects (`effects.ruleset:553-576`) give such an attacker a cap
  of 12 rounds, plus 12 at 11 or more hit points and 12 more at 21 or more (`MinHitPoints`, the unit's current hit
  points, `common/requirements.c:4383`), so a full-health Knights breaks off after 12 rounds, Cavalry after 24, Armor
  after 36, and a wounded one sooner. At the cap both units live.
- **Bombard range 1.** `bombard_max_range` is back to 1 (`actions.ruleset:169`), as in sandbox.
- README.civ45, the ruleset summary and the two flags' help texts say the same in the player's words.

### What stock Freeciv 3.2 cannot express (observed in the source)

| Wanted (reference game, spec 2.5 and 2.6) | Freeciv 3.2 | Where |
|---|---|---|
| Collateral hits a limited number of units (5 to 7) with a damage cap per unit (about half to 70 %) | Bombard hits every reachable unit on the tile with the same rate; the only floor is 1 hit point | `server/unithand.c:4545-4546`, `server/unittools.c:387-392` |
| Siege units are immune to collateral | Whether a unit can be hit is its class's reachability, shared with "Attack"; nothing per action or per flag | `is_unit_reachable_at` at `server/unithand.c:4546`; `Unreachable` class flag, `units.ruleset` class section |
| The siege unit fights the top defender and does collateral in the same attack | Bombard is its own action and ends the turn; the attack and the bombardment are two different actions on two turns | `Action_Success_Actor_Move_Cost` effect; `doc/README.actions:774-792` |
| Withdrawal is a chance to escape the killing blow | `Combat_Rounds` is a fixed cap on rounds, read for the attacker only; a defender never withdraws | `server/unittools.c:329-332`, `doc/README.effects:324-326` |
| The AI knows the odds change with the cap | `win_chance()` has no rounds parameter, so the AI's attack odds and Freeciv's defender choice assume a fight to the death | `common/combat.c:332,478` |
| Lua could do the rest | Lua can cut hit points but not read them, so a script cannot keep damage non-lethal or make a withdrawal roll | `common/scriptcore/tolua_game.pkg:58-66`, `server/scripting/api_server_edit.c:592-598` |

### Tests

`scripts/civ45-rules-test.sh ~/freeciv-builds/qt --data port/freeciv/data` passes 18/18 on the new ruleset
(`logs/civ45-rules-20261017-153316`): the eight slice 1 cases and ten new ones. A Howitzer bombards a three-unit animal
stack and all three live, then a Warriors beats that stack's defender (so the stack was wounded; a Warriors against a
full-health Warriors is a coin toss, against one at 1 hit point it wins about 99.9 % of fights); a Catapult may not
bombard a lone unit; a Bomber two tiles away may not bombard while an adjacent one may, and its target lives; a
Musketeers attacking a Musketeers leaves exactly one of them dead; a Knights attacking a Musketeers, which it cannot
kill within 12 rounds, leaves both alive; and `effects.unit_bonus` reads `Combat_Rounds` 0, 12 and 24 for a
Musketeers, a Knights and a Dragoons. The same test against the slice 1 ruleset (the installed copy,
`--data ~/freeciv-builds/qt/share/freeciv`, `logs/civ45-rules-20261017-153441`) gives 11/18: the seven cases that
depend on this slice fail, and in it the Warriors' attack on the unwounded stack ended undecided at 15 rounds with all
three units still there. The actions go through the real enablers (`Unit:perform_action` refuses a disabled action,
`server/scripting/api_server_edit.c:366-424`).

### Autogames

`scripts/test.sh` gained `--lua FILE` (a script loaded before the game starts) and `--extra CMD` (a server command in the
setup), and `scripts/civ45-combat-log.lua` logs every attack-type action, unit lost and city taken;
`scripts/civ45-combat-summary.py LOG` counts them. Four 200-turn games, 10 AIs, seeds 42/42, the slice 1 rules from the
installed copy against the new rules from the fork:

| | slice 1, peace allowed | slice 2, peace allowed | slice 1, diplomacy off | slice 2, diplomacy off |
|---|---|---|---|---|
| log | `logs/test-qt-20261017-153525` | `logs/test-qt-20261017-153528` | `logs/test-qt-20261017-153826` | `logs/test-qt-20261017-153829` |
| ended | allied victory, turn 149 | allied victory, turn 149 | turn limit, 200 | turn limit, 200 |
| attack-type actions | 8 Attack | 5 Attack, 5 Bombard 2 | 237 Attack, 1 Collect Ransom | 183 Attack, 1 Bombard 2, 1 Collect Ransom |
| fights left undecided (no unit lost) | not counted | not counted | 81 of 237 (34 %) | 39 of 183 (21 %), all by Withdraws units |
| attacks by Withdraws units | 0 | 0 | 50, 24 undecided | 66, 39 undecided |
| attackers that died | 3 | 3 | 33 | 38 |
| units killed in combat | 3 | 5 | 157 | 145 |
| siege bombardments | 0 | 5, one barbarian Cannon, the same city, turns 144 to 148 | 0 | 1, a Cannon, turn 194, a field stack of two |
| cities changing hands | 1 | 2 | 10 | 16 |
| wall time | about 150 s | about 150 s | 122 s | 124 s |

With diplomacy allowed both games ended at turn 149 by allied victory: the ten AIs had all allied, and in 150 turns the
only fighting was barbarians against the Mayas and the Thai. That is a finding about the autogame, not the slice (issue
below). In that little fighting the risk from the plan's table showed at once: in the slice 2 game a barbarian Cannon
next to the Maya city Wak Kab'nal (two defenders) used "Bombard 2" on five consecutive turns, 144 to 148, and never
attacked; in the slice 1 game the same barbarians sent Musketeers in to attack and die. The default AI takes a bombard
action whenever one is enabled, before it considers "Attack" (`ai/default/aitools.c:855-864`, and
`dai_select_tile_attack_action` tests `ACTRES_BOMBARD` before `ACTRES_ATTACK`, `ai/default/daiunit.c:459,495`), and
nothing in it values the wounds it inflicts or sends another unit in afterwards (observed; the only bombard-aware
code elsewhere is a "dummy" defence estimate, `ai/default/daimilitary.c:597`).

With diplomacy off the ten AIs fought for 200 turns, and the to-the-death rule shows in the fights. In the slice 1 game
81 of 237 attacks (34 %) ended with both units alive at the 15-round cap. In the slice 2 game 39 of 183 (21 %) did,
every one of them an attack by a Withdraws unit (39 of the 66 such attacks), and no fight between other units was left
undecided (observed: an attack during which no unit was lost, counted from the log). More attackers died (38 against
33) and more cities changed hands (16 against 10), which fits attacks that always resolve (derived; one pair of games on
the same seeds, so the difference is suggestive, not measured). The AIs built almost no siege: one Cannon did one
"Bombard 2" (turn 194, a field stack of two) and two attacks on lone units, so in these games the risk did not bite;
it will once the roster gives the AI siege lines to build (slice 10). Nothing in the four logs is a Lua error.

### Open

- The AI and siege (issue 83): the default AI bombards a stack every turn instead of attacking, and does not follow a
  bombardment with an attack by another unit. Options, in order of cost: keep "Bombard 2" off the AI's menu (an
  `"AI", ..., "Player"` requirement is not available for this; a Lua-free way is unknown), make the AI's attackers
  prefer wounded stacks (engine, `ai/default`), or accept it and let the harness's chooser play the siege.
- Tuning: the rates 5/10/14/20 and the 12-rounds-per-10-hit-points cap are placeholders until there is a roster (slice
  10) and a one-strength number per unit (plan decision 7).
- Allied victory ends an autogame around turn 150 on these seeds (issue 84); `--extra "set diplomacy DISABLED"` is the
  workaround used here.


## 7. Victory slice: six ways to win (2026-10-17, patch 0009)

Built from `notes/freeciv45/design/victory.md` (PR 77) as issue 92. Line numbers are the fork's at commit `be05401`
(upstream S3_2 `44e6898` plus patches 0001 to 0009).

### What the ruleset says now

| Win | Rule | Where |
|---|---|---|
| Conquest | Every rival dead or surrendered: the server's own rule, nothing set | `server/srv_main.c:524-546` |
| Domination | Hold 60 % of the land tiles and 50 % of all citizens for 3 turns running, checked from turn 100; Lua on `turn_begin` walks the map and the cities and calls `edit.player_victory` | `data/civ45/script.lua`, `fc45_domination_check` (the constants `FC45_DOM_*` at its top) |
| Culture | `victory_min_points` 8000 and `victory_lead_pct` 50 (sandbox 20000 and 100, which no player reached, design note 2.3) | `data/civ45/game.ruleset:390-397` |
| Space | `victories` keeps SPACERACE and `endspaceship` is written out as ENABLED: the ship must arrive | `game.ruleset:930-932` |
| Alliance | `victories` keeps ALLIED: the last alliance standing wins together (a vote waits for later slices, design note 2.5) | `game.ruleset:930` |
| Score | `endturn` 475; at the start of that turn Lua names the living civ with the highest `civilization_score` the winner, so the game ends with "Scenario victory to the X" instead of the turn-limit notice. The first civ found wins a tie | `game.ruleset:932`; `script.lua`, `fc45_score_winner` |

The domination run counters are one scalar global per player (`fc45_dom_run_<id>`), which the server saves with the
game; the test reads them back through `_G`. Barbarians and animals never count (`fc45_is_civ`).

### What stock Freeciv cannot express

- No requirement or setting reads a land or citizen share (`doc/README.effects:58-119`, design note 2.2), hence the Lua
  walk, which costs one pass over the map and all cities per turn from turn 100: measured on the turn-400 save of the war game below (1,275 land tiles, 493 citizens, 11 civs), a server run that performs the count 100 times took 0.31 s longer than one that performs it 0 times, so about 3 ms per turn (`logs/walk/`, the minimum of two runs each; Freeciv's Lua has no `os.clock`, so the server's wall time is the only clock). The war game itself averaged 1.2 s per turn, so the walk is below the noise.
- Lua cannot see alliances or the AI's attitude (no diplstate getter in `common/scriptcore/tolua_game.pkg` or
  `server/scripting/tolua_server.pkg`, design note 2.5), so domination is per player (allies do not pool) and a
  diplomatic vote is not written.
- The server's score winner at `endturn` is only a ranking (`server/score.c:417-429`, written with `--ranklog`), so
  the named winner is Lua's; there is no `endvictory` setting in 3.2.

### Tests

`scripts/civ45-rules-test.sh ~/freeciv-builds/qt --data port/freeciv/data`: 24/24 Lua cases plus four shell checks
(`logs/civ45-rules-20261017-154955`): the settings strings, every living civ qualifies at thresholds 0 and none at
60/50 on turn 5, the script's land count equals an independent count of non-oceanic tiles, a real check leaves every run
counter at 0, and the four `game.ruleset` keys. With `--extra "set endturn 6"` (the test runs at turn 5 and ends at
turn 6, not turn 12 as the design note assumed) the test logs the civ with the best score and the server's
"Scenario victory to the Mayas." names the same one (`logs/civ45-rules-20261017-155506`).
`scripts/harness-test.sh` still passes (`logs/harness-civ45-20261017-155025`); its control check and `scripts/test.sh`
now accept a game that ends by any victory line, not only the turn limit (issue 84's first point).

### Autogames

Two games to turn 475, 10 AIs, seeds 42/42, data from the fork:

| Game | `test.sh` flags | End | Leader's land and culture at the end |
|---|---|---|---|
| Default rules | none | Turn 152, allied victory to all ten living AIs (as in slice 2, issue 84); 5.5 minutes | Mursilis, 224 land tiles of about 1,275 (18 %), culture 1,985 |
| Diplomacy off | `--extra "set diplomacy DISABLED"` | Turn 437 (year 2011), "Game ended in cultural domination victory for Mursilis"; 8.9 minutes | Mursilis, 322 land tiles (25 %), culture 12,900 against 7,397 for the next civ |

Logs: `logs/test-qt-20261017-155025` and `logs/test-qt-20261017-155028` (final saves; land is the save's `landarea` divided by 1,000, the total from the test's land count). Observed: no AI came near the 60 % land threshold, so the domination rule never fired, and with diplomacy off the culture win arrived 38 turns before the score would have decided it; the two leaders' `history` values stood at 2,100, the top of the ten. Inferred: 8000 points with a 50 % lead is reachable by the strongest AI in a 10-player game by the early 2000s, which is about the pace the design note asked for; whether it is right for a human game is untested. The turn-limit path (score winner at 475) has only been seen in the rules test with `endturn` 6.

### Open

- The design note's five questions for John, built here with its recommended values: the domination thresholds
  (60 % land, 50 % citizens, 3 turns) against the spec's "about 65 % plus a population lead"; whether allies should
  win domination jointly (needs an engine getter or the `DiplRel` trick); `endturn` 475 as the shipped default;
  culture 8000 and a 50 % lead now, before the culture slice changes the pace; and whether the score winner should be
  announced through Lua at all.
- Culture and domination numbers are untuned (see the autogame); re-tune with roadmap row 8 and after slice 10.

## 8. Slice 3, upgrades and the draft: what was built and what was seen (2026-10-17, patch 0010)

Built from `notes/freeciv45/design/units-and-upgrades.md` section 1 (the upgrade rule and the three draft units) and
`notes/freeciv45/in-freeciv.md` 4.2 (the draft and whip workarounds) as issue 106. Line numbers are the fork's at
commit `c499bd2` (upstream S3_2 `44e6898` plus patches 0001 to 0010).

### What the ruleset says now

| Rule | Freeciv form | Where |
|---|---|---|
| Upgrades keep veteran levels | `upgrade_veteran_loss` 0 and `autoupgrade_veteran_loss` 0 (sandbox: 1 each). The server passes them to `transform_unit` | `data/civ45/game.ruleset:132,135`; `server/unithand.c:264`, `server/unittools.c:451` |
| Upgrade price unchanged | `2 * missing + missing^2 / 20`, missing = new cost less half the old unit's cost (`Unit_Shield_Value_Pct` -50 for "Upgrade Unit"), halved after Invention | `common/unittype.c:1731`; `effects.ruleset:5458-5464,579-586` |
| Draft units | Levy (Bronze Working, 2/2, 10 shields, 10 hp), Militia (Gunpowder, 8/8, 20, 20 hp), Conscripts (Conscription, 14/14, 25, 20 hp): `pop_cost 1`, a new `Draft` user flag, `obsolete_by "None"`, no roles, and four negated `Gov` reqs (Anarchy, Republic, Democracy, Federation), so they are raised under Tribal, Despotism, Monarchy, Communism or Fundamentalism | `units.ruleset:56,1181-1318` |
| The whip | Three `Unit_Shield_Value_Pct` rows (+250, +100, +70) on top of sandbox's -50 for "Disband Unit Recover", so a disbanded Levy, Militia or Conscripts is worth 30 shields whatever it cost: a citizen and the unit's shields become 30 shields in the build | `effects.ruleset:5450-5492`; `common/unit.c:222` (the value), `server/unithand.c:5745` (added whole to `shield_stock`) |

The draft units use one strength for attack and defence, as the design note's roster will (decision 7); the
rest of civ45 still has two values. No unhappiness follows a draft or a whip (in-freeciv.md 4.2, "Draft anger",
is not built); see "Open".

### What stock Freeciv cannot express

- Lua cannot build a unit or shrink a city (`tolua_server.pkg:117-254`), so the citizen cost of a draft is seen only
  through the server's own build path, in the autogame's `city_size_change` signal (reason `unit_built`), and the
  whip's 30 shields are read from a save (`disbanded_shields`, reset when a build completes, `server/cityturn.c:3545`).
- The whip still takes a turn: the city builds the Levy at the turn's end, and the player disbands it next turn.
  Sandbox's instant buy is gold only. A draft unit the city cannot afford (size 1) is refused at build time
  (`server/cityturn.c:2873-2881`).
- Nothing limits drafts per turn or per empire; the spec's 1 to 5 a turn and "keep 5 citizens" wait for a Lua
  `unit_built` handler that can at least report, not refuse.

### Tests

`scripts/civ45-rules-test.sh ~/freeciv-builds/qt --data port/freeciv/data`: 28/28 Lua cases and ten shell checks
(`logs/civ45-rules-20261017-162002`). New: the three draft units carry the flag; a Levy can be raised with Bronze
Working and a Militia only once Gunpowder is known (`Player:can_build_direct`, which reads the `Gov` reqs too); the
Tester founds a city of its own on free grassland or plains (`edit.create_city` refuses glacier, the map's free
rows, and any tile within `citymindist` of a city), upgrades a hardened Phalanx there through "Upgrade Unit" to a
Musketeers (the chain's end with Gunpowder known) that is still hardened, for exactly 105 gold (2 × 30 + 900 / 20,
missing 40 − 10); and a Levy disbanded into the build is gone, with the runner reading 30 `disbanded_shields` from
the first autosave after the test. The runner also greps the two veteran keys and the three `pop_cost` lines.
On the installed slice 1 copy (the control) 13/21 Lua cases pass: the draft cases stop at "the ruleset has the Levy, Militia and Conscripts draft units", the victory cases skip, and all nine ruleset greps fail, so the runner exits 1 as it should (`logs/civ45-rules-20261017-162442`). `scripts/harness-test.sh`: passes (`logs/harness-civ45-20261017-162245`), nothing in it changed.

### Autogame

One 300-turn game, 10 AIs, seeds 42/42, diplomacy off, with `scripts/civ45-draft-log.lua`
(`logs/test-qt-20261017-162434`); the slice 2 war game (`logs/test-qt-20261017-153829`, same seeds, 200 turns) is
the control. Observed:

| What | Count |
|---|---|
| Draft units built | 129 (106 Militia, 23 Conscripts, no Levy), the first at turn 152, by seven of the ten AIs (39 by one) |
| City size after the draft | 2: 37, 3: 35, 4: 18, 5: 26, 6 to 9: 13 |
| Draft units disbanded into a build by the AI | 12 Militia (beside 129 Phalanxes and 10 others it recycled on its own) |
| Draft units alive at turn 300 | 59 |
| Cities at turn 200 | 87, mean size 3.9, 21 % at size 1 or 2; control 87, 3.9, 20 % |
| Cities at turn 300 | 93, mean size 4.5, 19 % at size 1 or 2 |

Inferred: the AI never raises a Levy because it prices a citizen as the food to grow it back
(`ai/default/daicity.c:712-735`), which dwarfs 10 shields; a Militia at 8/8 for 20 shields is worth a citizen to it
from the turn Gunpowder arrives. It drafts from cities of size 3 to 5 as often as from size 2, and the city-size
profile at turn 200 is the control's, so "the AI drafts its cities small" (the roadmap's risk) did not show in 300
turns. The 12 Militia it disbanded into builds got the 30 shields each, by the AI's ordinary habit of recycling
units it no longer wants, not as a whip. The game ended at turn 300 with "Scenario victory to the Hittites": the
runner sets `endturn` 300, so the victory slice's score winner fired, as designed.

### Open

- The design note's question 1 (three draft units spanning the eras, or one per era) and the government list are
  decision 9 in the plan. The governments stand in for a civic until roadmap row 8.
- Draft anger and a draft limit (spec 2.4, in-freeciv.md 4.2) are not built: issue 107. Built later as patch 0024, section 13.
- The AI's use is as the autogame shows; nothing in the default AI knows what a draft is for (it treats a Levy as a
  cheap unit that happens to cost a citizen: `ai/default/daicity.c:712-735` prices the citizen in food, `:790` refuses
  it when the city is too small).

## 9. Tech slice: the tree in seven eras (2026-10-17, patch 0011)

Built from `notes/freeciv45/design/tech-tree.md` (PR 96) as issue 109, ahead of the roster (slice 10) because the
roster's new units sit behind techs only this tree adds (Hunting, Archery, Machinery, Compass). Line numbers are
the fork's at commit `af1367e` (upstream S3_2 `44e6898` plus patches 0001 to 0011).

### What the ruleset says now

| Rule | Freeciv form | Where |
|---|---|---|
| Seven eras | `[techclass_*]` sections Ancient, Classical, Medieval, Renaissance, Industrial, Modern, Information with `cost_pct` 100, 100, 110, 120, 130, 140, 150; every advance names its era in `class` | `data/civ45/techs.ruleset:49-76`, each `[advance_*]` |
| 92 advances | 86 of civ45's 89 kept, 3 dropped (Ruler Apotheosis, Nanomaterials, Labor Union), 6 added (Agriculture, Hunting, Archery, Machinery, Compass, Printing) with fallback icons (`graphic_alt` of a related tech) until the tileset draws them | `techs.ruleset`; `scripts/tech-tree-check.py --ruleset` compares names, prerequisites and classes with the design tables |
| Prerequisites | The design's tables; six changed from civ45's (Physics, Magnetism, Navigation, Atomic Theory, Genetic Engineering, Fusion Power) | the design note's "Re-homed" section |
| Re-homed unlocks | Altar to The Divine Ruler at Monarchy, Space Elevator and its Tether at Superconductors, Shakespeare's Theatre at Printing, Barracks at Warrior Code (they had no tech), Mech. Inf. at Robotics, irrigation at Agriculture | `buildings.ruleset:266,1265,1525,2285`; `units.ruleset:1404`; `terrain.ruleset:1263` |
| Cost | `Linear`: `base_tech_cost` 10 × the techs needed counted with the tech itself (`common/tech.c:230-243`, `advance_req_iterate` yields the tech too) × the era's `cost_pct` × `Tech_Cost_Factor` 3. A root tech costs 30, Gunpowder (tier 17) 648, Fusion Power (tier 70) 3,195. The design counted the tech itself out (612 and 3,150); its note is corrected in this slice | `scripts/civ45-rules-test.lua`, `fc45_tech_test_run` |

### What stock Freeciv cannot express

- Nothing in this slice: eras, costs per era and prerequisites are all stock 3.2 ruleset data. Lua has no getter for a
  tech's class (`common/scriptcore/tolua_game.pkg`, module Tech_Type), so the runner greps the file for the seven
  classes and the 92 `class` lines, and the research observer maps techs to eras from the design note.

### Tests

`scripts/civ45-rules-test.sh ~/freeciv-builds/qt --data port/freeciv/data`: 32/32 Lua cases and eleven shell checks
(`logs/civ45-rules-20261017-163826`). New: the six techs exist and the three are gone (`find.tech_type`), and the
Tester's cost for Alphabet, Gunpowder and Fusion Power through `Player:tech_cost` is 30, 648 and 3,195; the runner
counts the classes and advances. `scripts/tech-tree-check.py --buildings ... --ruleset port/freeciv/data/civ45/techs.ruleset`
passes. On the installed slice 1 copy (the control) 13/22 Lua cases pass, the tech and draft cases fail at their first check, and the runner's eleven greps fail, so it exits 1 as it should (`logs/civ45-rules-20261017-163628`). `scripts/harness-test.sh` passes (`logs/harness-civ45-20261017-163625`).

### Autogame

One 400-turn game, 10 AIs, seeds 42/42, diplomacy off, with `scripts/civ45-tech-log.lua`
(`logs/test-qt-20261017-163447`, AI skill level Easy, the server default); the victory slice's 475-turn game (`logs/test-qt-20261017-155028`,
same seeds, the old 89-tech tree with no era costs) is the control, read from its saves' `[research]` tables. Observed:

| Era | First AI to learn one of its techs | Median AI | AIs that reached it by turn 395 |
|---|---|---|---|
| I | turn 13 | 23 | 11 of 11 |
| II | 44 | 61 | 11 |
| III | 148 | 177 | 11 |
| IV | 205 | 234 | 10 |
| V | 302 | 348 | 6 |
| VI, VII | nobody | | 0 |

| Techs known per AI | New tree (of 92) | Old tree (of 89) |
|---|---|---|
| Turn 200 | 18 to 24 | 15 to 36 |
| Turn 400 | 31 to 44 | 56 to 59 |

The design's test plan asked for era IV by turn 200 and era VII by turn 400 from the best AI. Era IV came at 205;
era VII is out of reach: the best AI held 44 techs at turn 400 against 56 to 59 on the old tree, and the game ended at
turn 400 with the score winner (the runner's `endturn`). Inferred: the per-era `cost_pct` is not the main brake,
since the old tree's flat costs reached only era V to VI by turn 400 too; these AIs' science output is. The curve
is kept as designed and this pace is the evidence for decision 10; if John wants era VII reachable in a 475-turn
game, the lever is `cost_pct` for V to VII or `sciencebox`, measured again after the roster and the economy slices
change what the AI builds.

### Open

- The design note's four questions for John are decision 10 in the plan: Archery in era II; the three dropped techs;
  the `cost_pct` curve; themed names for Physics, Medicine and Electricity.
- The six new techs have borrowed icons until civ45-tileset draws `a.agriculture`, `a.hunting`, `a.archery`,
  `a.machinery`, `a.compass` and `a.printing`.
- Players start with no tech, so nobody irrigates before Agriculture (30 bulbs); the AI's opening was not
  measured separately.

## 10. Roster slice: 76 units with one strength and class counters (2026-10-17, patch 0012)

Built from `notes/freeciv45/design/units-and-upgrades.md` (PR 90) as issue 111, after the tech slice gave it Hunting,
Archery, Machinery and Compass. Line numbers are the fork's at commit `c89dbfe` (upstream S3_2 `44e6898` plus patches
0001 to 0012). The ruleset was generated from the design's tables by a script kept outside the repo; the tables are
the source, `units.ruleset` the result.

### What the ruleset says now

| Rule | Freeciv form | Where |
|---|---|---|
| 76 unit types | The design's 72 (46 kept, 11 renamed, 16 new, with Settlers, Workers, Migrants, Engineers, Caravan, Freight, Diplomat, Spy and the three draft units among them) plus civ45's Fanatics, Leader, Barbarian Leader and Storm. Dropped: Jaguar Warrior, Immortal, Alpine Troops, Crusaders, Mechanic (Engineers take its Heal Unit enabler) | `data/civ45/units.ruleset`, 76 `[unit_*]`; `actions.ruleset:959` |
| Renames keep the rule name | `name` is the shown name, `rule_name` the old one: Phalanx shows as Spearmen, Legion as Swordsmen, Elephants as War Elephants, Armor as Tank, Nuclear as Atom Bomb, Mech. Inf. as Mechanized Infantry, Helicopter as Gunship, AWACS as Radar Plane, AEGIS Cruiser as Missile Cruiser, SSBN as Missile Submarine, ICBM as Nuclear Missile; saves, the nuclear effects and the test scripts keep loading | each renamed `[unit_*]`; `effects.ruleset:531,541` (`UnitType Nuclear`) |
| New units borrow art | `graphic` is `u.<name>` for the tileset session to draw; `graphic_alt` is the template's sprite (Scout from Explorer, Axemen from Phalanx, Horse Bowmen from Horsemen, War Galley from Trireme, Macebearers from Legion, Longbowmen and Crossbowmen from Archers, Trebuchet from Catapult, Grenadiers from Musketeers, Ship of the Line from Frigate, Infantry, Machine Gunners and Air Defence Infantry from Riflemen, Armoured Cars and Main Battle Tank from Armor, Jet Fighter from Fighter) | the 16 new `[unit_*]` |
| One strength | `attack = defense` everywhere except attack 0 (Scout, Explorer, Transport, Carrier, Machine Gunners, Air Defence Infantry, Radar Plane) and defence 0 (Cruise Missile, Atom Bomb, Nuclear Missile); the runner checks it | `units.ruleset`; `scripts/civ45-rules-test.sh` |
| Hit points and firepower | 10 in eras I to III, 20 in IV to VI, 30 for Tank, Battleship, Carrier and every era VII unit; `firepower = 1` throughout (Battleship and Carrier had 2) | each `[unit_*]` |
| Class flags | Melee, Archer, Mounted, Gun, Siege, Armour, Naval, Recon: 8 more user flags, 35 of 50 used | `units.ruleset:57-64` |
| Counters | Two `bonuses` rows on the unit that has the counter, both keyed on the target class: `DefenseMultiplierPct` N (its defence when that class attacks it) and `DefenseDividerPct` N (the target's defence when it attacks that class). Spearmen and Pikemen 100 against Mounted; War Elephants 50 against Mounted; Riflemen 25 against Mounted; Axemen, Macebearers and Crossbowmen 50 against Melee; Horsemen, Horse Bowmen, Knights, Dragoons and Cavalry 50 against Siege; Grenadiers 50 against Gun; Mechanized Infantry 50 and Gunship 100 against Armour; Machine Gunners 50 against Gun and Melee (defence only); Catapult −50 against Mounted (defence only); Air Defence Infantry ×4 against AirAttacker, Destroyer ×2 against Submarine and Missile Cruiser ×5 against AirAttacker as before | `common/combat.c:645-690` (`defense_multiplication`: the defender's rows against the attacker's flags, then the attacker's rows against the defender's flags, lines 681-684); each `[unit_*]` |
| City attack | `Attack_Bonus` with `UnitType` and `CityTile Center Tile`: Swordsmen, Tank, Marines and Main Battle Tank 25; Catapult, Ship of the Line and Cruiser 50; Trebuchet, Cannon, Artillery, Battleship and Howitzer 100. Armoured Cars get 50 with `CityTile Center Tile FALSE` (the open field) | `effects.ruleset:2160-2323` |
| City and terrain defence | `Fortify_Defense_Bonus` (fortified units and units in cities): Archers and Longbowmen 50 in a city, Longbowmen 25 on Hills, Partisan 50 on Hills and in Forest | `effects.ruleset`, the `effect_*_defence_*` sections |
| Walls | `Defend_Bonus` 100 from City Walls keyed on the attacker's Melee, Archer, Mounted or Siege flag, the Siege one with `UnitType Howitzer FALSE`; the old row keyed on the Ground class is gone, so Gun, Armour, air and sea attackers get no wall against them. Great Wall and the 50 every city gives against Ground attackers are unchanged | `effects.ruleset:2122-2158` |
| Resources | `Extra` reqs at `City` range on the extras the map has: Iron for Swordsmen, Macebearers, Crossbowmen, Knights, Cannon, Ship of the Line and Ironclad (Coal too), Ivory for War Elephants, Oil for Armoured Cars, Tank, Main Battle Tank, Mechanized Infantry, Gunship, the aircraft and the modern warships; Horses, Copper, Aluminium and Uranium wait for slice 4 | each `[unit_*]` `reqs` |
| Transports | Trireme 2 (Land, Small Land), Caravel 1 (Small Land, fuel 0, no longer a barbarian boat: the server wants room for a leader and one man), Galleon 3, Frigate 1, Transport 8, Carrier 4 (air, missiles, helicopters), Missile Cruiser 2 and Missile Submarine 8 missiles | each `[unit_*]` |

### What stock Freeciv cannot express

- The counter as the design wrote it. The note said the divider row goes on every unit of the target class keyed on
  a flag of the holder; the server reads the attacker's rows against the defender's flags (`common/combat.c:681-684`),
  so that row cancelled the multiplier. The first build scored 8 Pikemen wins of 20 against War Elephants
  (`logs/civ45-rules-20261017-165742`); with both rows on the holder it scored 14 of 20. The design note's row is
  corrected in this slice, and no counter flags are needed.
- A negative `DefenseMultiplierPct` (Catapult −50 against Mounted) loads; its effect in a fight was not measured.

### Tests

`scripts/civ45-rules-test.sh ~/freeciv-builds/qt --data port/freeciv/data`: 38/38 Lua cases and thirteen shell checks
(`logs/civ45-rules-20261017-170246`). New: the eleven renames (`Unit_Type:name_translation`), the five dropped and the
sixteen new types (`find.unit_type`), the class flags (`has_flag`), twenty fights of War Elephants (strength 8,
Mounted, no Withdraws) against Pikemen (6, doubled to 12) on open grassland, won by the Pikemen at least 11 times
(0.998 with the counter, 0.006 without; 14 observed), and City Walls read through `effects.unit_bonus` on units standing in
Testerburg before and after `City:create_building`: +100 for Warriors and Catapult, +0 for Musketeers and Howitzer. The
upgrade case now expects 225 gold (Musketeers 60 less half of Spearmen's 20, missing 50). The runner counts the 76 types,
checks attack = defence unless one is 0 and firepower 1, and the four walls sections. On the installed slice 1 copy
(the control) 13/25 Lua cases pass with 12 failures and the runner exits 1 (`logs/civ45-rules-20261017-170443`).
`scripts/harness-test.sh` passes (`logs/harness-civ45-20261017-165453`).

### Autogame

Two 400-turn games, 10 AIs, seeds 42/42, with `scripts/civ45-combat-log.lua`, read by `scripts/civ45-roster-summary.py`
(units alive by era of the design's tables, largest stack, attackers and casualties by type): one with diplomacy off
(`logs/test-qt-20261017-170345`, the score winner at turn 400) and one with it allowed
(`logs/test-qt-20261017-170345-73055`, cultural domination victory at turn 379). No Lua errors in either.

| | Diplomacy off | Diplomacy allowed |
|---|---|---|
| attack-type actions, whole game | 894 | 477 |
| in the first 200 turns (slice 2's 200-turn war game: 183) | 315 | 198 |
| units killed in combat, whole game | 1,857 lost in all | 1,241 lost in all |
| cities taken | 40 | 19 |
| attackers, most used | Galleon 268, Spearmen 155, Riflemen 111, Frigate 92, Axemen 71, Pikemen 71, Musketeers 65 | Spearmen 204, Musketeers 85, Galleon 64, Pikemen 58, Militia 25, Dragoons 11, Axemen 9 |
| killed in combat, most | Spearmen 295, Galleon 139, Settlers 117, Workers 97, Pikemen 48, Frigate 45, Axemen 34 | Spearmen 247, Workers 105, Settlers 63, Galleon 51, Pikemen 48, Musketeers 22, Dragoons 20 |

Units alive by era (the design's tables; "other" is Settlers, Workers, Engineers, Diplomat, Caravan, Storm and the like):

| Turn | Diplomacy off: I / II / III / IV / V / other | Diplomacy allowed: I / II / III / IV / V / other |
|---|---|---|
| 100 | 82 / 0 / 0 / 0 / 0 / 66 | 85 / 0 / 9 / 0 / 0 / 125 |
| 200 | 105 / 3 / 47 / 35 / 0 / 76 | 211 / 2 / 10 / 15 / 0 / 132 |
| 300 | 4 / 2 / 3 / 70 / 48 / 67 | 86 / 1 / 45 / 151 / 0 / 149 |
| final | 0 / 2 / 0 / 27 / 146 / 72 (turn 401) | 25 / 0 / 11 / 236 / 49 / 132 (turn 379) |

Observed: the AI builds and fights with the new units (Axemen, Horse Bowmen, Knights, Pikemen, Dragoons appear in both
games); nobody fielded an era VI or VII unit, as the tech pace of section 9 predicts (era V from turn 302). Spearmen are
the AI's most used attacker and most killed unit in both games: with attack equal to defence the default AI sends its
cheapest unit, which is the first evidence on decision 7. Galleons (strength 4) made 268 attacks in the war game,
hunting boats. The largest stack was 42 units on one tile at turn 379 in the diplomacy game (a port holding most of
one player's 144 Galleons); 11 at turn 200. Era IV units carried the middle game in both (236 alive at the end of the
diplomacy game).

### Open

- The design note's five questions for John are decision 11 in the plan: three draft units, hit points by era,
  Cruiser and Ship of the Line both kept, Alpine Troops and Crusaders dropped, Transport cargo 8.
- Sprites for civ45-tileset: `u.scout`, `u.axemen`, `u.horse_bowmen`, `u.war_galley`, `u.macebearers`, `u.longbowmen`,
  `u.crossbowmen`, `u.trebuchet`, `u.grenadiers`, `u.ship_of_the_line`, `u.infantry`, `u.machine_gunners`,
  `u.armoured_cars`, `u.main_battle_tank`, `u.air_defence_infantry`, `u.jet_fighter` (and the matching `m_`/`f_` sound
  tags, which fall back to the generic ones).
- The late roster (eras VI and VII) is untested in play until the AI reaches it; the counters above era III
  (Grenadiers, Mechanized Infantry, Gunship, Machine Gunners) were checked only by the loader.
- The AI's choice of attackers under one strength (decision 7), and the Catapult's negative row.
- Horses, Copper, Aluminium and Uranium gating waits for the resources slice (4).

## 11. Great people slice: seven kinds, residents, deeds, golden ages and the AI rule (2026-10-17, patch 0013)

Built from `notes/freeciv45/design/great-people.md` (PR 101) as issue 113, the last of the five rules slices the
design session specified. Line numbers are the fork's at the slice's commit (upstream S3_2 `44e6898` plus patches
0001 to 0013). The ruleset data was generated from the design's tables by a script kept outside the repo.

### What the ruleset says now

| Rule | Freeciv form | Where |
|---|---|---|
| Seven kinds | Unit types Great Sage, Builder, Magnate, Virtuoso, Oracle, Commander, Spymaster: class Land, cost 240, `pop_cost` 1, strength 0, 10 hit points, 2 moves, no upkeep, no reqs, flags `NonMil`, `NoVeteran`, `NoBuild`, `Unbribable`, `AddToCity`, `GreatPerson` (the Builder adds `HelpWonder`, the Spymaster `Diplomat`); art borrowed from Diplomat, Engineers, Caravan, Leader and Spy until `u.great_*` are drawn | `units.ruleset:65` (the flag, 36 of 50 used), `:3687-3952` |
| Points | `User_Effect_3` per building at `City` range: 1 for Temple, Library, Marketplace, Colosseum (shown as Amphitheater), Courthouse; 2 for University, Bank, Cathedral, Factory, Police Station; 3 for Research Lab, Stock Exchange, Mfg. Plant; 2 for each of 29 wonders and each Resident. `User_Effect_4` 100 under a golden age. `scripts/gp-points-check.py` diffs the 49 rows with `script.lua`'s table | `effects.ruleset:5742-6133` |
| Pool and birth | Each turn every city adds its points times (100 + percent) / 100 to `fc45_gp_pool_<city id>`; at 150 + 75 × the player's births so far, one great person is born on the city tile, its kind drawn in proportion to the city's sources, and the pool resets. The first player to research Philosophy, Theology, Economics or Electricity gets a Sage, Oracle, Magnate or Builder in the capital | `script.lua:635-792`, `:879-892` |
| Settling | "Join City" by a great person needs no Resident of its kind in the city (seven enablers with a `target_reqs` row; the stock enabler excludes `GreatPerson`); the `pop_cost` citizen is the server's, the Resident building Lua's | `actions.ruleset:1391-1491`; `script.lua:800-809` |
| Residents | Seven `Improvement` buildings with `MinYear 9999 World` so nobody builds them (`edit.create_building` ignores reqs): Sage +25 % science, Builder +3 shields on the centre, Magnate +3 trade on the centre and +25 % gold, Virtuoso `History` 3 and +25 % luxury, Oracle `Make_Content` 2, Commander `Veteran_Build` 1, Spymaster `Spy_Resistant` 50 and `Incite_Cost_Pct` 100; each gives 2 points | `buildings.ruleset:2504-2664`; `effects.ruleset:6134-6220` |
| Deeds | "User Action 3" (Great Deed, target Self, consumes the actor): Sage `edit.give_tech(owner, nil, 0, true, ...)` (the cheapest tech, `free_tech_method`); Magnate 100 + 30 × city size gold, doubled in a foreign city; Virtuoso `edit.add_city_history(city, 400)`; Oracle founds the Sanctum (`SmallWonder`, `Make_Content` 1 at Player range, `History` 3), moved from any city that had it; Commander `Unit:transform(type, -1)` on every own unit on the tile, one level up. Enablers: Sage, Virtuoso and Oracle in a city whose tile is not foreign (`DiplRelTile`), the Magnate in any city, the Commander anywhere. Builders use the native "Help Wonder" (240 shields), Spymasters the diplomat actions (the `UnitFlag Diplomat` embassy enabler already exists at `actions.ruleset:651`, so the design's extra row was not needed). Great people are kept out of "Disband Unit Recover" | `actions.ruleset:496-506`, `:1150`, `:1163`, `:3075-3113`; `effects.ruleset:6221-6236` (the Sanctum); `script.lua:811-857` |
| Golden age | "User Action 4" (Pledge a Golden Age, Self, consumes): pledges count per player; at 1 + the ages so far the "Golden Age" small wonder is created in the capital (else the first city) for 10 turns: `Output_Inc_Tile` 1 shield and 1 trade at Player range, `User_Effect_4` 100, `No_Anarchy`. `turn_begin` removes it when `fc45_golden_until_<player>` is reached | `buildings.ruleset:2688`; `effects.ruleset:6237-6270`; `script.lua:859-877` |
| AI | Each `turn_begin`, for every AI civ: pledge with as many great people as the next age needs when none runs; Sage, Virtuoso and Magnate do their deed where they stand; Oracle and Commander settle where no Resident of their kind is, else deed; Builders after 10 turns and Spymasters after 20 settle; a refused deed falls through to settling. All through `edit.perform_action`, so the same enablers as a human | `script.lua:894-940` |
| Persistence | Every counter is a scalar global named by an integer id (`fc45_gp_key` formats it with `%d`), so the saved script state, which is Lua source, parses back | `script.lua:706-711` |

### What stock Freeciv cannot express

- Nothing the design needed was missing. Two things the design did not say: ids reach Lua as floats, so a global
  named `fc45_gp_pool_187.0` was written to the first saves and would not have loaded back (fixed by formatting
  the id; the runner now checks the autosave); and `game.turn()` inside a `turn_begin(n)` handler is n − 1, so the
  golden age's end is stored from that value and compared with the handler's turn.
- A great person's native uses are not logged by the script: whether an AI Builder ever did "Help Wonder" in the
  autogames is unknown (the log shows its Builders pledging or settling).

### Tests

`scripts/civ45-rules-test.sh ~/freeciv-builds/qt --data port/freeciv/data`: 50/50 Lua cases and fifteen shell checks
(`logs/civ45-rules-20261017-173438`). New, in Testerburg at turn 5: a Library gives 1 point and a University 3;
a Sage's deed adds one known tech, a Magnate's 100 + 30 × size gold, a Virtuoso's 400 culture, an Oracle's the
Sanctum and one more content citizen; a Commander on a free tile drills two green Warriors to level 1; one pledge
starts a golden age in the capital until turn + 10 with `User_Effect_4` 100, a second pledge counts 1 of 2. A turn
later: a pool set to 148 bears a Great Sage and resets, the age ends when its turn comes, the Sage settles (size +1,
Resident Sage), a second Sage is refused by the enabler but does its deed. The runner diffs the points table with the
effect rows and finds `fc45_golden_count_0=1` in the first autosave after the pledge. On the installed slice 1 copy
(the control) the great people cases are skipped with Testerburg and the runner exits 1 (`logs/civ45-rules-20261017-173612`).
`scripts/harness-test.sh` passes (`logs/harness-civ45-20261017-172311`).

### Autogame

Two 400-turn games, 10 AIs, seeds 42/42, the ruleset's own `FC45GP` log lines read by `scripts/civ45-gp-summary.py`:
diplomacy allowed (`logs/test-qt-20261017-172633`) and off (`logs/test-qt-20261017-172633-75950`), both to the score
winner at turn 400, no Lua errors.

| | Diplomacy allowed | Diplomacy off |
|---|---|---|
| great people born (first at turn) | 74 (130) | 49 (124) |
| from points / first to a tech | 70 / 4 | 45 / 4 |
| by kind | Oracle 17, Magnate 17, Virtuoso 15, Spymaster 15, Sage 6, Builder 3, Commander 1 | Oracle 16, Spymaster 14, Sage 9, Magnate 5, Virtuoso 4, Builder 1 |
| used by the AI | 67 (7 born in the last turns unused) | 43 (6 unused) |
| how | deed 36, settle 11, pledge 20 | deed 21, settle 10, pledge 12 |
| turns from birth to use | median 1, 63 of 67 within 20, longest 44 | median 1, 42 of 43 within 20, longest 50 |
| golden ages begun | 15 (four civs reached their second) | 11 (one second) |
| deeds seen | 16 trade missions of 280 to 490 gold, 8 masterworks, 6 Sanctums, 6 techs (Archery twice, Printing, ...) | 7 Sanctums, 4 masterworks, 6 techs (The Corporation, Sanitation, Railroad, Economics, Compass, ...), 4 missions |
| counters in the final save | 185 globals, the 4 first-to-tech keys | 131, 4 |

Observed: the pace is 5 to 7 great people per civ in 400 turns, inside the design's 3 to 6 without wonders and 8 to
12 with them; the first arrives around turn 125. Oracles and Spymasters dominate because temples and courthouses
are what the AI builds first; Builders and Commanders are rare (factories come late, Statue of Zeus and Sun Tzu are
their only early sources). The AI rule spends almost everything the turn after birth; the long waits are Spymasters
the native diplomat code walked out of their city, which settle only when back in one. Every civ's first great
person becomes a golden age (the rule pledges whenever none runs and the next age needs no more people than are
at hand), which is the first thing to tune.

### Open

- The design note's five questions for John are decision 12 in the plan: the point values held twice (kept, with the
  checker); Residents lost on capture like other buildings; great people out of "Disband Unit Recover"; pledges of
  any kind; the Spymaster without a deed of its own.
- The AI's first great person always pledges; a rule that keeps the first Sage or Magnate for its deed may serve it
  better (section 6 of the design note, order 1).
- Sprites for civ45-tileset: `u.great_sage`, `u.great_builder`, `u.great_magnate`, `u.great_virtuoso`,
  `u.great_oracle`, `u.great_commander`, `u.great_spymaster`, `b.resident_*` (seven), `b.sanctum`, `b.golden_age`.
- Points from specialists (design note section 1) stay out until Lua can count them; the Commander from combat
  waits for slice 6.

## 12. John's decisions 9 to 12 applied: the tree, the curve, the roster and the great people (2026-10-17, patch 0014)

John answered the design notes' questions on 2026-10-17 (plan decisions 9 to 12, issue 115). Six answers kept the
first build (three draft units; hit points 10/20/30; both Cruiser and Ship of the Line; point values in the effect
rows and the Lua table; no recycling of great people, the Builder's Help Wonder stays; the Spymaster with the
native diplomat actions as its deed). The rest changed the fork at commit 9c9b25c, lines cited there.

### What the ruleset says now

| Answer | Built | Where |
|---|---|---|
| Archery in era I | `class = "Ancient"`; Archers stay in the era I roster table, Horse Bowmen keep era II (they need Horseback Riding too) | `civ45/techs.ruleset:186` |
| Horses gate the mounted units now | `[extra_horses]` and `[resource_horses]` (shield 1, trade 1) on Grassland and Plains; `"Extra", "Horses", "City"` on Horsemen, Horse Bowmen, Chariot, Zealots, Knights, Dragoons and Cavalry, as Iron and Oil already were | `terrain.ruleset:599,815,1114,2164`; `units.ruleset:1671-1965` |
| Keep the three techs, 95 in all | Labor Union (Communism + Mobile Warfare, Modern), Nanomaterials (Plastics + Computers, Information), Ruler Apotheosis (Polytheism + Mysticism, Classical); the Altar needs Ruler Apotheosis, the Space Elevator and its Tether Nanomaterials, Women's Suffrage Labor Union (it was at Conscription); Mechanized Infantry stays at Robotics, which the checker's re-homed table had already settled | `techs.ruleset:545,720,906`; `buildings.ruleset:1260,1520,2307,2478` |
| The steep curve | `cost_pct` 100, 150, 175, 200, 225, 250, 275 by era (the first build: 100, 100, 110, 120, 130, 140, 150); eras V to VII lowered to 200 on 2026-10-18 (issue 167, tech-tree.md section 1) | `techs.ruleset:49-75` |
| Themed unlocks | Physics: Siege Workshop (`Veteran_Build` 1 for `UnitFlag Siege`); Medicine: Apothecary (`Health_Pct` 30, `HP_Regen` 10 for Land units in the city); Electricity: Telegraph Office (`Max_Trade_Routes` 1) | `buildings.ruleset:2504-2572`; `effects.ruleset:6272-6306` |
| Alpine Troops and Crusaders back, nation-neutral | Alpine Troops at Tactics: strength 14, cost 100, move 1, `IgTer`, `Gun`, obsolete by Infantry (civ45's 7/4 under one strength). Zealots at Monotheism: strength 8, cost 50, move 2, `Mounted`, `Withdraws`, Horses and no Iron, obsolete by Knights (civ45's Crusaders under a name that belongs to no faith) | `units.ruleset:1197,1834` |
| Transport cargo 4 | `transport_cap = 4` | `units.ruleset:3149` |
| Residents stay with a captured city | Settling records the kind in `fc45_gp_res_<city id>` (`Sage;` and so on) and the owner in `fc45_gp_res_owner_<city id>`; `fc45_gp_residents_restore` re-creates every recorded Resident the city lacks, from the `city_transferred` signal (conquest only, `server/citytools.c:2145`) and from a `turn_begin` sweep over cities whose owner no longer matches the record (trades, incitement and civil war emit no signal) | `script.lua:776,807-824` |
| Golden ages need different kinds | Seven "Pledge of the <Kind>" small wonders (`MinYear 9999`, cost 1); seven enablers for "User Action 4", one per `UnitType Great <Kind>`, each with `Building "Pledge of the <Kind>" Player FALSE`; a pledge short of the age raises its marker in the capital, the age removes all seven; the AI pledges with one great person of each kind it has not pledged, when it holds enough of them | `buildings.ruleset:2780-2940`; `actions.ruleset:3109-3170`; `script.lua:895-957,960` |

### The cost curve

Bulbs = 10 × (tier + 1) × `cost_pct` / 100 (`common/tech.c:273`, a double) × `Tech_Cost_Factor` 3, with the
tiers of `notes/freeciv45/design/tech-tree.md`. The reference game's own era ratios are not in this note's sources
(2.4 cites the science pages, not a cost table), so "rise steeply era over era" is the target and the numbers are
ours: +50 points after era I, then +25 per era, chosen so that each era's average costs about twice the one before
from era IV on and the last era's cheapest tech costs more than the first era's dearest by a factor of 45.

| Era | Techs | Tier range | `cost_pct` | Cheapest to dearest, bulbs | Era average | Ratio to era I | First build's average |
|---|---|---|---|---|---|---|---|
| I | 14 | 0 to 2 | 100 | 30 to 90 | 47 | 1 | 47 |
| II | 14 | 1 to 8 | 150 | 90 to 405 | 199 | 4.2 | 132 |
| III | 12 | 5 to 14 | 175 | 315 to 787 | 542 | 11.5 | 341 |
| IV | 10 | 10 to 22 | 200 | 660 to 1,380 | 1,068 | 22.7 | 641 |
| V | 14 | 20 to 49 | 225 | 1,417 to 3,375 | 2,372 | 50 | 1,370 |
| VI | 15 | 28 to 59 | 250 | 2,175 to 4,500 | 3,635 | 77 | 2,036 |
| VII | 16 | 49 to 70 | 275 | 4,125 to 5,857 | 5,161 | 110 | 2,815 |

(The first build's column uses the same tiers with 100 to 150; the three restored techs sit at tiers 5, 59
and 65.) The rules test pins Alphabet 30, Gunpowder 1,080 (tier 17, 200%) and Fusion Power 5,857 (tier 70,
275%; 710 × 2.75 = 1,952.5, times 3).

### What stock Freeciv 3.2 cannot express (observed in the source)

- A city-range requirement has no Lua test: `Player:can_build_direct` is `can_player_build_unit_direct`
  (`common/unittype.c:1968`), which treats city-range requirements as possible, so the Horses gate is a shell
  check over the ruleset text and the autogame is the only evidence in play.
- `edit.transfer_city` and the diplomatic, incitement and civil-war transfers emit no `city_transferred`; only
  `unit_conquer_city` does (`server/citytools.c:2145`). The turn sweep covers the rest a turn late.
- An action enabler cannot count buildings, so "different kinds" is seven markers and seven enablers rather than
  one rule; the markers are small wonders so that `Building ... Player` can read them, which means they go with
  the capital when it falls.

### Tests

`scripts/civ45-rules-test.sh ~/freeciv-builds/qt --data port/freeciv/data`: 57/57 Lua cases and eighteen shell
checks (`logs/civ45-rules-20261017-183334`); the control on the installed slice 1 ruleset gives 13/25 and exit 1
as before. New cases: the three restored techs exist and the costs above; Alpine Troops (`Gun`, `IgTer`) and
Zealots (`Mounted`, `Withdraws`); the Altar and Women's Suffrage need their techs again; the three buildings'
effects measured on a Catapult and the city before and after (`Veteran_Build` 0 to 1, `Health_Pct` 0 to 30,
`Max_Trade_Routes` 2 to 3); a second Sage cannot pledge the age a Sage has pledged while the marker stands; a
settled Sage is recorded (`Sage;`) and re-created after its Resident is removed; a second city of the Tester's
settles a Great Oracle, is handed to another player and still has its Resident Oracle a turn later with the record
pointing at the new owner. Shell: 95 advances each in a class, the seven `cost_pct` values, 85 unit types with one
strength and firepower 1, Transport cargo 4, the Horses extra, resource and seven requirements.
`scripts/tech-tree-check.py --ruleset --buildings`: PASS, 95 techs, deepest tier 70, with the design note's tiers
refilled.

### Autogames

Three 400-turn games, 10 AIs, seeds 42/42, with `scripts/civ45-tech-log.lua`: the previous build (patch 0013,
diplomacy off, `logs/test-qt-20261017-180813`) against this one with diplomacy off
(`logs/test-qt-20261017-182517`) and on (`logs/test-qt-20261017-182519`), read by `scripts/civ45-tech-summary.py`
and `scripts/civ45-gp-summary.py`. The diplomacy-on game ended at turn 155 with an allied victory, so its pace
(era V at turn 125 through tech trading) is not comparable and only its great people count below.

| Era | Before: first AI, median | After, diplomacy off: first AI, median |
|---|---|---|
| I | 15, 26 | 11, 18 |
| II | 58, 83 | 44, 70 |
| III | 110, 170 | 82, 154 |
| IV | 142, 233 | 131, 178 |
| V | 180, 269 | 232, 254 |
| VI | 327, 357 | 367, 388 |
| VII | nobody | nobody |
| Techs per AI at the end | 55 to 60 (one outlier at 27) | 57 to 59 |

Observed: the curve moves era V and VI first arrivals later by 52 and 40 turns, but the AIs end with the same
number of techs, because the early eras went faster (era IV's median 55 turns earlier) and the late-game science
of these AIs outruns the costs. Inferred: the steep curve shapes when the eras arrive more than how many techs a
game holds, and era VII in 400 turns is still out of reach for the Easy AI, as section 9 found on the gentle curve.

| Great people | Before | After, diplomacy off | After, diplomacy on (155 turns) |
|---|---|---|---|
| Born | 48 | 50 | 15 |
| Used by the AI within 20 turns | 46 of 47 | 43 of 43 | 14 of 14 |
| Settled | 9 | 8 | 0 |
| Golden ages begun | 12 (10 first, 2 second) | 8 (all first) | 7 (all first) |
| Pledges short of an age | 2 | 0 | 0 |
| Cities held by a player other than their founder at the end | 36 of 95 | 30 of 93 | |
| Residents re-created for a new owner | | 0 | 0 |

Observed: no AI reached a second golden age under the different-kinds rule in 400 turns, where two did before:
the AI pledges only when it holds enough great people of distinct kinds at once, and it spends each one within a
turn or two, so it never does. The settled cities (Bangkok, Oneida, Wien) were none of the 30 that changed hands,
so the Residents-on-capture rule ran in no game; the handover case in the rules test is its evidence.

### Open

- The AI never reaches a second golden age (issue 121): let it pledge one great person of a kind it
  lacks whenever no age runs and the marker will wait, or lower the second age to two of any kind for the AI.
- Residents re-created after a conquest are untested in play; the signal path and the sweep are tested by the
  rules test only.
- The pledge markers and the Golden Age fall with the capital, forgetting the pledges.
- Art: `b.siege_workshop`, `b.apothecary`, `b.telegraph_office`, `b.pledge`, `u.zealots` and the `ts.horses`
  tile are borrowed until civ45-tileset draws them.

## 13. Draft and whip unrest, and a draft limit (2026-10-17, patch 0024)

Issue 107: a draft or a whip now costs the city content for a while, and an empire can draft only a few times a
turn, as the reference behaviour in the "Production, whipping and drafting" paragraph of section 2 has it (one
unhappy face for 10 turns per whip, three per draft, 1 to 5 drafts a turn by map size). Lines are the fork's at
the patch.

### What the ruleset says now

| Rule | Built | Where |
|---|---|---|
| Unrest | Building a draft unit (the `Draft` flag) adds faces to the city for `FC45_UNREST_TURNS` 10 turns: the Levy (the whip of eras I to III) 1, Militia and Conscripts (the draft) 3. Faces of several drafts add up, to 7 at most | `script.lua`, `fc45_draft_unit_built`, `fc45_unrest_add` |
| How a face is held | Three hidden buildings, Draft Unrest 1, 2 and 4 (genus Improvement, `MinYear 9999`, cost 1, no upkeep, sabotage 0), with `Make_Content` -1, -2 and -4; Lua keeps the set that sums to the faces. Each city's record is a scalar global `fc45_unrest_<city id>` = `"<expiry turn>:<faces>;..."`, so it survives a save | `buildings.ruleset`, `effects.ruleset` (end), `script.lua` `fc45_unrest_apply` |
| Expiry | `turn_begin` drops the expired entries of every recorded city and sets its buildings to match | `fc45_unrest_turn` |
| No escape by selling | Improvements can be sold (`common/improvement.c:1114`, `is_building_sellable` is genus Improvement); `building_lost` (emitted for a sale, `server/citytools.c:3000-3006`, and for disasters) puts an unrest building back at once. `edit.remove_building` emits nothing (`api_server_edit.c:769-786`), so Lua's own removals do not loop | `fc45_unrest_lost` |
| The draft limit | One draft a turn per 400 land tiles of the map, 1 to 5 (`fc45_draft_limit`, counted once and saved as `fc45_draft_limit_n`; the default map of 10 to 12 players at `tilesperplayer` 100 gives 3). The draft that reaches the limit gives the player the hidden "Draft Quota" small wonder in its capital, which Militia and Conscripts require to be absent (`"Building", "Draft Quota", "Player", FALSE` in their `reqs`), so no other city of that player completes one in the same turn's end; `turn_begin` removes it. The Levy has no quota: whipping is limited by citizens, not by the empire | `units.ruleset` (Militia, Conscripts), `script.lua` `fc45_draft_counted` |
| Logged | `FC45UNREST turn T <city> of <player> +F by <unit>, now N` and `FC45DRAFTS turn T <unit> of <player> is draft n of L this turn` in the server log | `script.lua` |

### The limit of the unrest

`Make_Content` is summed over the city's effects and a sum at or below zero makes nobody content
(`common/city.c`, `citizen_content_buildings`: `while (faces > 0 && ...)`). So the unrest cancels content that a
Temple, Colosseum, Cathedral or wonder would give, and does nothing to the base content citizens
(`citizen_base_mood`, from `City_Unhappysize` and the empire size at Player range). A city with no content
buildings feels no unrest at all; one with a Temple loses the Temple's one or two faces first. No requirement
type lets a city-range effect lower the base content number (`EFT_CITY_UNHAPPYSIZE` and the empire-size effects
are read with `get_player_bonus`, `common/city.c:2174-2195`, so a city requirement never holds there), and no other
effect turns content citizens unhappy outside nationality and military units. A full malus needs an engine
change (a city-range content penalty applied to the base mood); filed as an issue for civ54 or upstream.
`notes/freeciv45/in-freeciv.md` 4.2 "Draft anger" had rated it "sees the malus"; that row now says what holds.

### Refusing a draft needs no engine change

Lua cannot cancel a build, but a requirement can: the quota is a Player-range small wonder that the draft units'
`reqs` exclude, so for the rest of that turn's end `city_build_unit` finds the unit "no longer available", tells
the owner and keeps the city's shields and its choice (`server/cityturn.c:2848-2860`); the city completes the draft
on a later turn when the quota allows it. The design's question ("whether a refusal needs an engine change") is
answered no. Barbarians skip that check (the same lines), but they never build draft units.

### Seen in play

Two 300-turn games, 10 AIs, seeds 42/42, diplomacy off, read from the server log (`FC45DRAFT`, `FC45WHIP`,
`FC45UNREST`, `FC45DRAFTS`) and `scripts/civ45-combat-summary.py`:

| | Without the unrest (patch 0021's rules) | With it |
|---|---|---|
| Draft units built | 25 (18 Conscripts, 6 Militia, 1 Levy) | 50 (35 Conscripts, 14 Militia, 1 Levy) |
| Disbanded into a build | 26 | 23 |
| Unrest after a draft | | 50 entries; the city then held 1 face once, 3 faces 35 times, 6 faces 11 times and the cap of 7 three times |
| Turns at the draft limit (3 on this map) | | 1 (49 counted drafts: 43 turns with one, 5 with two, 1 with three) |
| Attacks, cities changing hands | 568, 36 | 595, 36 |

The two games part ways early (the extra buildings change the AI's choices), so the draft counts are two samples,
not a measured effect; the AI does not know the unrest exists and drafts as before. The limit bit once in 300
turns: the default AI rarely drafts more than once a turn.

### Open

- A full malus on base content needs an engine change (filed).
- "The city keeps at least 5 citizens" for a draft and "at most half the population" for a whip are not built
  (filed); they are a design call because they would end most of the AI's drafting.
- The AI does not weigh the unrest when it drafts.
- A captured city keeps its unrest under its new owner (the record is the city's, and a building lost in the
  capture is put back).

