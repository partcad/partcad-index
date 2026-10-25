#!/usr/bin/env python3
"""Split the packages of //pub into contiguous ranges, one per CI shard.

Reads the output of 'pc --no-ansi list packages -r' on stdin, where every
package is a line of its own starting with a tab and its path, and writes two
GitHub Actions outputs to stdout:

  matrix  the matrix of ".github/workflows/pub.yml", with one "shard" entry per
          range: {"n": 1, "of": 8, "packages": "//pub/a //pub/b ..."}
  count   how many packages there are in all

The ranges are of the sorted list, so neighbouring packages -- which usually
share their dependencies -- are tested by the same job, and they are as even in
length as the count allows.

'pc list packages' names the packages that have objects to list. A package
with nothing to test or render (a plugin, a material catalogue, a directory
that only groups others) is not in it, and needs no shard.
"""

import argparse
import json
import re
import sys

PACKAGE = re.compile(r"^\t(//pub(?:/\S*)?)(?:\s|$)")


def packages(listing):
    found = set()
    for line in listing.splitlines():
        match = PACKAGE.match(line)
        if match:
            found.add(match.group(1))
    return sorted(found)


def ranges(items, shards):
    shards = max(1, min(shards, len(items)))
    size, extra = divmod(len(items), shards)
    result, start = [], 0
    for n in range(shards):
        end = start + size + (1 if n < extra else 0)
        result.append(items[start:end])
        start = end
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shards", type=int, required=True)
    parser.add_argument("--os", required=True, help="JSON list of runner images")
    parser.add_argument("--python", required=True, help="JSON list of Python versions")
    args = parser.parse_args()

    found = packages(sys.stdin.read())
    if not found:
        sys.exit("No package found in the listing on stdin: did 'pc list packages' change its format?")

    split = ranges(found, args.shards)
    matrix = {
        "os": json.loads(args.os),
        "python-version": json.loads(args.python),
        "shard": [{"n": n + 1, "of": len(split), "packages": " ".join(r)} for n, r in enumerate(split)],
    }
    print("matrix=" + json.dumps(matrix, separators=(",", ":")))
    print("count=%d" % len(found))
    for n, r in enumerate(split):
        print("shard %d/%d: %d packages, %s .. %s" % (n + 1, len(split), len(r), r[0], r[-1]), file=sys.stderr)


if __name__ == "__main__":
    main()
