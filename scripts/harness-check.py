#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Check a harness game: what the server applied, against the questions, the chooser's answers and the saves.

usage: harness-check.py GAMEDIR --player NAME [--turns N] [--skip ID,...] [--bad ID,...] [--control DIR]

GAMEDIR holds harness/applied.jsonl (the server's record of every decision), chooser.jsonl (the chooser's
log), questions/ (a copy of every question, from harness-chooser.py --keep) and the server's saves. Prints
one line per check and exits 0 only if they all pass. --control names a game played on the same seeds
without the hook; the player's final score in both games is printed, but not checked.
"""
import argparse
import csv
import glob
import gzip
import json
import os
import re
import sys


def id_set(text):
    return {int(x) for x in text.split(",") if x.strip()}


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def table(lines, start):
    """A secfile table: 'key={"a","b",...' on lines[start], one row per line, then '}'."""
    def parse(line):
        return next(csv.reader([line], escapechar="\\", doublequote=False))
    header = parse(lines[start].split("=", 1)[1].lstrip("{"))
    rows, i = [], start + 1
    while lines[i] != "}":
        rows.append(dict(zip(header, parse(lines[i]))))
        i += 1
    return rows


def read_save(path, player):
    """The save's turn, the player's cities, and the player's research row."""
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")
    turn, section, pooled, mine = None, "", True, None
    team = number = None
    cities, research = [], {}
    for i, line in enumerate(lines):
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            m = re.fullmatch(r"player(\d+)", section)
            mine = None if m is None else int(m.group(1))
            continue
        if section == "game" and line.startswith("turn="):
            turn = int(line[5:])
        elif line.startswith('"team_pooled_research",'):
            pooled = line.split(",")[1] == "TRUE"
        elif mine is not None and line == 'name="%s"' % player:
            number = mine
        elif mine is not None and mine == number and line.startswith("team_no="):
            team = int(line[8:])
        elif mine is not None and mine == number and line.startswith("c={"):
            cities = table(lines, i)
        elif section == "research" and line.startswith("r={"):
            research = {int(r["number"]): r for r in table(lines, i)}
    return turn, cities, research.get(team if pooled else number)


def final_score(gamedir, player):
    """The player's score in the game-over save, or None."""
    finals = glob.glob(os.path.join(gamedir, "*final.sav*"))
    if not finals:
        return None
    with gzip.open(finals[0], "rt", encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")
    section, number = "", None
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
        elif re.fullmatch(r"player\d+", section) and line == 'name="%s"' % player:
            number = section[6:]
        elif number is not None and section == "score" + number and line.startswith("total="):
            return int(line[6:])
    return None


def main():
    ap = argparse.ArgumentParser(description="Check a harness game.")
    ap.add_argument("gamedir")
    ap.add_argument("--player", required=True)
    ap.add_argument("--turns", type=int)
    ap.add_argument("--skip", type=id_set, default=set())
    ap.add_argument("--bad", type=id_set, default=set())
    ap.add_argument("--control")
    args = ap.parse_args()
    results = []

    def check(name, ok, detail):
        print("%s: %s, %s" % (name, "ok" if ok else "FAILED", detail))
        results.append(ok)

    applied = read_jsonl(os.path.join(args.gamedir, "harness", "applied.jsonl"))
    chooser = {r["id"]: r for r in read_jsonl(os.path.join(args.gamedir, "chooser.jsonl"))}
    questions = {}
    for path in glob.glob(os.path.join(args.gamedir, "questions", "q*.json")):
        with open(path, encoding="utf-8") as f:
            q = json.load(f)
        questions[q["id"]] = q

    # 1. One record per question, numbered from 1, for both kinds of decision.
    builds = [d for d in applied if d["kind"] == "build"]
    research = [d for d in applied if d["kind"] == "research"]
    check("decisions",
          [d["id"] for d in applied] == list(range(1, len(applied) + 1)) and builds and research
          and all(d["player"] == args.player for d in applied),
          "%d (%d builds, %d research)" % (len(applied), len(builds), len(research)))

    # 2. Each question's shape: 2 to 8 numbered options, the AI's pick first, no repeats, a status page.
    problems = []
    for d in applied:
        q = questions.get(d["id"])
        if q is None:
            problems.append("q%d: no copy" % d["id"])
            continue
        opts = q["options"]
        if not 2 <= len(opts) <= 8 or [o["n"] for o in opts] != list(range(1, len(opts) + 1)):
            problems.append("q%d: options numbered %s" % (d["id"], [o["n"] for o in opts]))
        if [o["ai"] for o in opts] != [True] + [False] * (len(opts) - 1):
            problems.append("q%d: the AI's pick isn't option 1 alone" % d["id"])
        if len({o["value"] for o in opts}) != len(opts) or not all(o["label"] and o["value"] for o in opts):
            problems.append("q%d: a repeated or empty option" % d["id"])
        if q["kind"] != d["kind"] or q["player"] != args.player or (q["city"] is None) != (q["kind"] == "research"):
            problems.append("q%d: kind, player or city doesn't match" % d["id"])
        if opts[0]["value"] != d["ai_value"]:
            problems.append("q%d: option 1 isn't the recorded AI pick" % d["id"])
        if "Cities (" not in q["state"] or "Research:" not in q["state"]:
            problems.append("q%d: no status page" % d["id"])
    sizes = [len(q["options"]) for q in questions.values()]
    check("questions", not problems and len(questions) == len(applied),
          "; ".join(problems[:5]) if problems else "%d, %d to %d options, status pages up to %d characters"
          % (len(questions), min(sizes, default=0), max(sizes, default=0),
             max((len(q["state"]) for q in questions.values()), default=0)))

    # 3. Every answer applied as given; the skipped and bad ones fell back to the AI's pick.
    problems, answered = [], 0
    for d in applied:
        c = chooser.get(d["id"], {})
        if d["id"] in args.skip:
            ok = d["fallback"] == "timeout" and d["choice"] == 1 and d["value"] == d["ai_value"]
        elif d["id"] in args.bad:
            ok = (d["fallback"] or "").startswith("bad answer") and d["choice"] == 1 \
                and d["value"] == d["ai_value"]
        else:
            ok = d["fallback"] is None and c.get("choice") == d["choice"] \
                and questions.get(d["id"], {}).get("options", [{}] * d["choice"])[d["choice"] - 1].get("value") \
                == d["value"]
            answered += ok
        if not ok:
            problems.append("q%d: applied %s (choice %d, fallback %s), chooser %s"
                            % (d["id"], d["value"], d["choice"], d["fallback"], c.get("action")))
    missing = sorted((args.skip | args.bad) - {d["id"] for d in applied})
    if missing:
        problems.append("no question %s to test a fallback on" % ",".join(map(str, missing)))
    check("answers", not problems,
          "; ".join(problems[:5]) if problems else "%d applied as answered; q%s timed out and q%s had a bad answer, "
          "both kept the AI's pick" % (answered, ",".join(map(str, sorted(args.skip))),
                                       ",".join(map(str, sorted(args.bad)))))

    # 4. In each save, a pick from an earlier turn is still in place, or the game changed it and the
    #    hook asked again that turn. Autosaves come at the start of a turn, before that turn's decisions.
    #    Every city a decision names must be in a later save under the same name, so a name the hook spelled
    #    differently from the game can't slip past.
    saves = sorted(glob.glob(os.path.join(args.gamedir, "*.sav*")))
    problems, in_place, reasked, last_turn, final_turn = [], 0, 0, 0, None
    seen = {}
    for path in saves:
        turn, cities, row = read_save(path, args.player)
        final = "final" in os.path.basename(path)
        if final:
            final_turn = turn
        for c in cities:
            seen.setdefault(c["name"], []).append(turn)
        before = [d for d in applied if d["turn"] < turn]
        now = [d for d in applied if d["turn"] == turn]
        state = [(c["name"], c["currently_building_name"], "build") for c in cities]
        if row is not None:
            state.append((None, row["now_name"], "research"))
        for city, current, kind in state:
            last = [d for d in before if d["kind"] == kind and d["city"] == city]
            if not last:
                continue
            if current == last[-1]["value"]:
                in_place += 1
            elif any(d["kind"] == kind and d["city"] == city for d in now):
                reasked += 1
            elif final:
                last_turn += 1
            else:
                problems.append("%s: %s %s is %s, the last pick was %s (q%d)"
                                % (os.path.basename(path), kind, city or "", current, last[-1]["value"],
                                   last[-1]["id"]))
    for d in applied:
        if d["kind"] == "build" and not any(t > d["turn"] for t in seen.get(d["city"], [])):
            problems.append("q%d: no later save has a city named %s" % (d["id"], d["city"]))
    check("saves", not problems and in_place > 0,
          "; ".join(problems[:5]) if problems else "%d saves: %d picks in place, %d changed by the game and asked "
          "again, %d changed in the last turn" % (len(saves), in_place, reasked, last_turn))

    # 5. Re-asks because the game changed a pick should be rare; many would mean picks don't stick.
    changed = [d for d in applied if d["reason"] == "changed"]
    check("re-asks", len(changed) <= max(2, len(applied) // 4),
          "%d of %d decisions came from the game changing a pick" % (len(changed), len(applied)))

    # 6. The game played every turn: the game-over save comes after the last turn.
    if args.turns is not None:
        check("game", final_turn == args.turns + 1, "game-over save at turn %s" % final_turn)

    # Not a check: how the player did against the same game without the hook.
    if args.control:
        print("score: %s %s with the chooser, %s in the control game (same seeds, no hook)"
              % (args.player, final_score(args.gamedir, args.player), final_score(args.control, args.player)))

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
