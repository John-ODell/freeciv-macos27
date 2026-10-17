#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Answer the Freeciv harness hook without a model.

At each build or research decision of the AI players named in FREECIV_HARNESS_PLAYERS, the server
(ai/default/daiharness.c, patch 0007) writes DIR/question.json and waits for DIR/answer.txt, one line
"ID CHOICE". This chooser answers with a random option (--mode random) or always option 1, the AI's own
pick (--mode first), and logs one JSON line per question to --log. --skip leaves the listed question ids
unanswered and --bad answers them with an option that doesn't exist, to exercise the server's fallbacks.
--keep saves a copy of every question. The chooser stops when the process --pid ends.

usage: harness-chooser.py DIR [--mode random|first] [--seed N] [--log FILE] [--keep DIR]
                              [--skip ID,...] [--bad ID,...] [--pid PID]
"""
import argparse
import json
import os
import random
import sys
import time


def id_set(text):
    return {int(x) for x in text.split(",") if x.strip()}


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def main():
    ap = argparse.ArgumentParser(description="Answer the Freeciv harness hook without a model.")
    ap.add_argument("dir")
    ap.add_argument("--mode", choices=("random", "first"), default="random")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--log")
    ap.add_argument("--keep")
    ap.add_argument("--skip", type=id_set, default=set())
    ap.add_argument("--bad", type=id_set, default=set())
    ap.add_argument("--pid", type=int)
    args = ap.parse_args()

    question = os.path.join(args.dir, "question.json")
    answer = os.path.join(args.dir, "answer.txt")
    rng = random.Random(args.seed)
    log = open(args.log, "a", encoding="utf-8", buffering=1) if args.log else None
    if args.keep:
        os.makedirs(args.keep, exist_ok=True)
    seen = set()

    while args.pid is None or alive(args.pid):
        try:
            with open(question, encoding="utf-8") as f:
                q = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            time.sleep(0.02)
            continue
        if q["id"] in seen:
            # Still waiting for the server to take the answer, or a skipped question.
            time.sleep(0.02)
            continue
        seen.add(q["id"])
        start = time.monotonic()
        if args.keep:
            with open(os.path.join(args.keep, "q%05d.json" % q["id"]), "w", encoding="utf-8") as f:
                json.dump(q, f, ensure_ascii=False, indent=1)

        n = len(q["options"])
        row = {"id": q["id"], "turn": q["turn"], "kind": q["kind"], "city": q["city"],
               "reason": q["reason"], "options": n, "mode": args.mode}
        if q["id"] in args.skip:
            row["action"] = "skip"
        else:
            if q["id"] in args.bad:
                choice = n + 1
                row["action"] = "bad"
            else:
                choice = 1 if args.mode == "first" else rng.randint(1, n)
                row["action"] = "answer"
                row["value"] = q["options"][choice - 1]["value"]
                row["why"] = "always the AI's pick" if args.mode == "first" else "random pick"
            row["choice"] = choice
            # Write it whole, then rename, so the server never reads half a line.
            with open(answer + ".tmp", "w", encoding="utf-8") as f:
                f.write("%d %d\n" % (q["id"], choice))
            os.replace(answer + ".tmp", answer)
        row["secs"] = round(time.monotonic() - start, 3)
        if log:
            log.write(json.dumps(row, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
