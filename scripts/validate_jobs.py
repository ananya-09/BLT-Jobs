#!/usr/bin/env python3
"""
Validate job listings and report any that need manual review.
Exits with code 1 if any jobs need review (useful for CI/CD).
"""

import json
import sys
from pathlib import Path

JOBS_JSON = Path(__file__).resolve().parent.parent / "data" / "jobs.json"


def main():
    if not JOBS_JSON.exists():
        sys.exit(1)

    data = json.loads(JOBS_JSON.read_text(encoding="utf-8"))
    needs_review = [j for j in data["jobs"] if j.get("needs_manual_review")]

    if not needs_review:
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
