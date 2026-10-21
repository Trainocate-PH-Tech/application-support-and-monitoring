"""Score each submitted line against the live regex challenge rules."""

import argparse
import re
import sys


VALID_LINE = re.compile(
    r'2026-10-21T10:1[5-9]:[0-5][0-9]Z '
    r'id=[^ ]+ level=(WARN|ERROR) env=prod service=checkout '
    r'host=app-0[12] path=/checkout status=5[0-9]{2} '
    r'duration_ms=([2-9][0-9]{3}|[1-9][0-9]{4}[0-9]*) '
    r'client=203\.0\.113\.8 request=[^ ]+ '
    r'code=(UPSTREAM_TIMEOUT|DB_DEADLOCK) '
    r'message="(payment timeout|deadlock detected|retry exhausted)"'
)


def count_lines(lines):
    """Count every line, including blank lines; remove only its line ending."""
    correct = incorrect = 0
    for line in lines:
        if VALID_LINE.fullmatch(line.removesuffix("\n").removesuffix("\r")):
            correct += 1
        else:
            incorrect += 1
    return correct, incorrect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_file", help="Path to the submitted evidence file")
    args = parser.parse_args()
    try:
        with open(args.evidence_file, encoding="utf-8") as evidence:
            correct, incorrect = count_lines(evidence)
    except (OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Total Correct: {correct}")
    print(f"Total Incorrect: {incorrect}")
    print(f"Score: {correct - incorrect}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
