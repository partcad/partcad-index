#!/usr/bin/env python3
"""Split the packages of //pub into contiguous ranges, one per CI shard.

Reads the output of 'pc --no-ansi list packages -r' on stdin, where every
package is a line of its own starting with a tab and its path, and writes two
GitHub Actions outputs to stdout:

  matrix  the matrix of ".github/workflows/pub.yml", with one "shard" entry per
          range: {"label": "1/6", "packages": "//pub/a //pub/b ..."}
  count   how many packages there are in all

A package under an '--own-shard' prefix goes to the shard of that prefix, one
shard per prefix whatever its size: that is for a subtree too large to share
one (LDraw). Everything else is split into at most '--shards' ranges of the
sorted list, so that neighbouring packages -- which usually share their
dependencies -- are tested by the same job. The ranges are balanced by how
long each package took, from '--weights' (a JSON object of package -> seconds,
measured from the job summaries of a run), and a package it does not name
counts as the median of those it does.

'pc list packages' names the packages that have objects to list. A package
with nothing to test or render (a plugin, a material catalogue, a directory
that only groups others) is not in it, and needs no shard.
"""

import argparse
import json
import re
import statistics
import sys

PACKAGE = re.compile(r"^\t(//pub(?:/\S*)?)(?:\s|$)")
DEFAULT_WEIGHT = 60


def packages(listing):
    found = set()
    for line in listing.splitlines():
        match = PACKAGE.match(line)
        if match:
            found.add(match.group(1))
    return sorted(found)


def under(package, prefix):
    return package == prefix or package.startswith(prefix + "/")


def ranges(items, weight, shards):
    """At most 'shards' contiguous ranges of 'items', the heaviest as light as it can be."""
    if not items:
        return []

    def fill(capacity):
        result, current, total = [], [], 0
        for item in items:
            if current and total + weight(item) > capacity:
                result.append(current)
                current, total = [], 0
            current.append(item)
            total += weight(item)
        result.append(current)
        return result

    low, high = max(weight(i) for i in items), sum(weight(i) for i in items)
    while low < high:
        middle = (low + high) // 2
        if len(fill(middle)) <= shards:
            high = middle
        else:
            low = middle + 1
    return fill(low)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shards", type=int, required=True, help="How many ranges for what has no shard of its own")
    parser.add_argument("--own-shard", action="append", default=[], metavar="PREFIX")
    parser.add_argument("--weights", help="JSON object of package -> seconds")
    parser.add_argument("--os", required=True, help="JSON list of runner images")
    parser.add_argument("--python", required=True, help="JSON list of Python versions")
    args = parser.parse_args()

    found = packages(sys.stdin.read())
    if not found:
        sys.exit("No package found in the listing on stdin: did 'pc list packages' change its format?")

    measured = {}
    if args.weights:
        with open(args.weights) as f:
            measured = {k: int(v) for k, v in json.load(f).items()}
    default = int(statistics.median(measured.values())) if measured else DEFAULT_WEIGHT

    def weight(package):
        return max(1, measured.get(package, default))

    own = {prefix: [p for p in found if under(p, prefix)] for prefix in args.own_shard}
    rest = [p for p in found if not any(under(p, prefix) for prefix in args.own_shard)]

    split = ranges(rest, weight, args.shards)
    shards = [("%d/%d" % (n + 1, len(split)), r) for n, r in enumerate(split)]
    shards += [(prefix.rsplit("/", 1)[-1], r) for prefix, r in own.items() if r]

    matrix = {
        "os": json.loads(args.os),
        "python-version": json.loads(args.python),
        "shard": [{"label": label, "packages": " ".join(r)} for label, r in shards],
    }
    print("matrix=" + json.dumps(matrix, separators=(",", ":")))
    print("count=%d" % len(found))
    for label, r in shards:
        # A shard of its own is not balanced by weight, and its packages are
        # mostly not in the weights, so an estimate for it would be invented.
        estimate = "" if "/" not in label else ", ~%.0f min on Linux" % (sum(weight(p) for p in r) / 60)
        print("shard %s: %d packages%s, %s .. %s" % (label, len(r), estimate, r[0], r[-1]), file=sys.stderr)


if __name__ == "__main__":
    main()
