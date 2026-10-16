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
