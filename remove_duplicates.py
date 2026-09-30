#!/usr/bin/env python3
"""Remove duplicate lines from a text file, keeping the first occurrence.

Usage:
    python remove_duplicates.py input.txt                # overwrite input.txt
    python remove_duplicates.py input.txt -o output.txt  # write to output.txt
    python remove_duplicates.py input.txt --ignore-case --strip
    python remove_duplicates.py input.txt --words        # dedupe words within each line
"""

import argparse
import sys


def dedupe_lines(lines, ignore_case=False, strip=False, keep_blank=False):
    """Return lines with duplicates removed, preserving original order."""
    seen = set()
    result = []
    for line in lines:
        key = line.rstrip("\r\n")
        if strip:
            key = key.strip()
        if ignore_case:
            key = key.casefold()
        if keep_blank and key.strip() == "":
            result.append(line)
            continue
        if key not in seen:
            seen.add(key)
            result.append(line)
    return result


def dedupe_words(lines, ignore_case=False):
    """Remove repeated words across the whole file, keeping the first occurrence."""
    seen = set()
    result = []
    for line in lines:
        kept = []
        for word in line.split():
            key = word.casefold() if ignore_case else word
            if key not in seen:
                seen.add(key)
                kept.append(word)
        result.append(" ".join(kept) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description="Remove duplicates from a text file.")
    parser.add_argument("input", help="Path to the input text file")
    parser.add_argument("-o", "--output", help="Output file (default: overwrite input)")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="Treat lines/words differing only in case as duplicates")
    parser.add_argument("-s", "--strip", action="store_true",
                        help="Ignore leading/trailing whitespace when comparing lines")
    parser.add_argument("-b", "--keep-blank", action="store_true",
                        help="Keep all blank lines instead of collapsing them")
    parser.add_argument("-w", "--words", action="store_true",
                        help="Remove duplicate words instead of duplicate lines")
    parser.add_argument("--encoding", default="utf-8", help="File encoding (default: utf-8)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding=args.encoding, errors="replace", newline="") as f:
            lines = f.readlines()
    except OSError as e:
        sys.exit(f"Error reading {args.input}: {e}")

    if args.words:
        cleaned = dedupe_words(lines, args.ignore_case)
    else:
        cleaned = dedupe_lines(lines, args.ignore_case, args.strip, args.keep_blank)

    # Make sure the last line ends with a newline so lines don't merge.
    if cleaned and not cleaned[-1].endswith(("\n", "\r")):
        cleaned[-1] += "\n"

    output_path = args.output or args.input
    try:
        with open(output_path, "w", encoding=args.encoding, newline="") as f:
            f.writelines(cleaned)
    except OSError as e:
        sys.exit(f"Error writing {output_path}: {e}")

    removed = len(lines) - len(cleaned) if not args.words else None
    if removed is not None:
        print(f"Done: {len(lines)} lines read, {removed} duplicates removed -> {output_path}")
    else:
        print(f"Done: duplicate words removed -> {output_path}")


if __name__ == "__main__":
    main()
