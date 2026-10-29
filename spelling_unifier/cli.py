"""Command-line interface for spelling-unifier."""
import argparse

from .core import dominant_style, find_variants, unify


def main(argv=None):
    ap = argparse.ArgumentParser(prog="spelling-unifier", description="Detect and unify US/UK spelling.")
    ap.add_argument("file")
    ap.add_argument("--to", choices=["us", "uk", "oxford", "auto"], help="rewrite to this style (auto = majority)")
    ap.add_argument("-o", "--output", help="output file (default: overwrite only with --in-place)")
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args(argv)
    with open(args.file, encoding="utf-8") as fh:
        text = fh.read()
    hits = find_variants(text)
    counts, major = dominant_style(hits)
    print("Spelling counts: " + ", ".join("%s=%d" % kv for kv in sorted(counts.items())) + "; majority style: " + major)
    if not args.to:
        minority = [h for h in hits if not (h[2].startswith(major[:2]) or (major == "oxford" and h[2] in ("uk", "us-ize")))]
        for pos, word, style, other in minority[:50]:
            line = text.count("\n", 0, pos) + 1
            print("  line %d: %s (%s) -> %s" % (line, word, style, other))
        return 1 if minority else 0
    target = major if args.to == "auto" else args.to
    new, changes = unify(text, target)
    for change, n in changes.most_common():
        print("  %s (x%d)" % (change, n))
    dest = args.output or (args.file if args.in_place else None)
    if dest:
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(new)
        print("%d change(s) written to %s" % (sum(changes.values()), dest))
    return 0
