#!/usr/bin/env python3
"""
Check whether a new job file is a duplicate of an existing job.
Outputs JSON result and exits with code 1 if duplicate, 0 otherwise.
"""

import json
import sys
from pathlib import Path

import frontmatter

JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"


def normalize_fingerprint(title, org, location):
    return "|".join([
        (title or "").lower().strip(),
        (org or "").lower().strip(),
        (location or "").lower().strip(),
    ])


def check_duplicate(new_job_path):
    new_path = Path(new_job_path)
    if not new_path.exists():
        print(f"Error: Job file not found: {new_job_path}", file=sys.stderr)
        sys.exit(1)

    new_post = frontmatter.load(str(new_path))
    new_fm = new_post.metadata
    new_fingerprint = normalize_fingerprint(
        new_fm.get("title"),
        new_fm.get("organization_name"),
        new_fm.get("location"),
    )

    existing_files = [
        f for f in JOBS_DIR.iterdir()
        if f.suffix == ".md" and f.name != "README.md" and f.name != new_path.name
    ]

    for file_path in existing_files:
        post = frontmatter.load(str(file_path))
        fm = post.metadata
        existing_fingerprint = normalize_fingerprint(
            fm.get("title"),
            fm.get("organization_name"),
            fm.get("location"),
        )
        if new_fingerprint == existing_fingerprint:
            print(json.dumps({
                "isDuplicate": True,
                "existingFile": file_path.name,
                "title": fm.get("title") or "Untitled",
                "organization": fm.get("organization_name") or "Unknown",
                "location": fm.get("location") or "Not specified",
            }))
            sys.exit(1)

    print(json.dumps({"isDuplicate": False}))
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check_duplicate.py <path-to-job-file>", file=sys.stderr)
        sys.exit(1)
    check_duplicate(sys.argv[1])
