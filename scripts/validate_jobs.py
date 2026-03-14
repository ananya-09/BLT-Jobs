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
        print("❌ Error: jobs.json not found. Run build_jobs.py first.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(JOBS_JSON.read_text(encoding="utf-8"))
    needs_review = [j for j in data["jobs"] if j.get("needs_manual_review")]

    if not needs_review:
        print("✅ All jobs validated successfully. No manual review needed.")
        sys.exit(0)

    print("\n⚠️  WARNING: The following jobs need manual review:\n", file=sys.stderr)
    for job in needs_review:
        print(f"   Job ID: {job['id']}", file=sys.stderr)
        print(f"   Title: {job['title']}", file=sys.stderr)
        print(f"   Organization: {job['organization_name']}", file=sys.stderr)
        print(f"   URL: {job.get('application_url', '')}", file=sys.stderr)
        print("   Reason: Possible scrape failure detected", file=sys.stderr)
        print("", file=sys.stderr)

    print(f"Total: {len(needs_review)} job(s) need manual review\n", file=sys.stderr)
    print("Action required:", file=sys.stderr)
    print("1. Visit the application URL to verify the job details", file=sys.stderr)
    print("2. Manually update the job markdown file in jobs/ directory", file=sys.stderr)
    print("3. Set 'needs_manual_review: false' once verified\n", file=sys.stderr)

    sys.exit(1)


if __name__ == "__main__":
    main()
