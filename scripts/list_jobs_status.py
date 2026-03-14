#!/usr/bin/env python3
"""
List all jobs with their review status.
Useful for getting an overview of the job board.
"""

import json
import sys
from pathlib import Path

JOBS_JSON = Path(__file__).resolve().parent.parent / "data" / "jobs.json"


def main():
    if not JOBS_JSON.exists():
        sys.exit(1)

    data = json.loads(JOBS_JSON.read_text(encoding="utf-8"))

    needs_review = sum(1 for j in data["jobs"] if j.get("needs_manual_review"))
    validated = data["count"] - needs_review

    print(f"Total: {data['count']} | Validated: {validated} | Needs review: {needs_review}")


if __name__ == "__main__":
    main()
