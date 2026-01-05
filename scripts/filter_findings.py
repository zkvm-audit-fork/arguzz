#!/usr/bin/env python3
import argparse
import csv
import shlex
from pathlib import Path


def has_missing_input_value(input_flags: str) -> bool:
    # Treat any --inX flag without a following value as invalid.
    tokens = shlex.split(input_flags)
    idx = 0
    while idx < len(tokens):
        tok = tokens[idx]
        if tok.startswith("--in"):
            if idx + 1 >= len(tokens):
                return True
            nxt = tokens[idx + 1]
            if nxt.startswith("--"):
                return True
            idx += 2
            continue
        idx += 1
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Filter findings.csv to drop cases with missing input values."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to findings.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to write filtered CSV",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"input not found: {args.input}")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    kept = 0
    dropped = 0

    with args.input.open(newline="") as infile, args.output.open(
        "w", newline=""
    ) as outfile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise SystemExit("input CSV has no header")
        if "input_flags" not in reader.fieldnames:
            raise SystemExit("input CSV missing 'input_flags' column")

        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            if has_missing_input_value(row.get("input_flags", "")):
                dropped += 1
                continue
            writer.writerow(row)
            kept += 1

    print(f"kept={kept} dropped={dropped} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
