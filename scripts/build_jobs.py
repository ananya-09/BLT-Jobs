#!/usr/bin/env python3
"""
Build data/jobs.json from jobs/*.md and data/seekers.json from seekers/*.md.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import frontmatter

from extract_salary import extract_salary

JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"
OUT_FILE = Path(__file__).resolve().parent.parent / "data" / "jobs.json"
SEEKERS_DIR = Path(__file__).resolve().parent.parent / "seekers"
SEEKERS_OUT_FILE = Path(__file__).resolve().parent.parent / "data" / "seekers.json"


def md_to_job(file_path):
    post = frontmatter.load(str(file_path))
    fm = post.metadata
    body = (post.content or "").strip()
    stem = file_path.stem

    def get(k, default=None):
        v = fm.get(k)
        if v is None or v == "":
            return default
        return v

    description = body or get("description") or ""
    description = description.strip()

    salary_range = get("salary_range") or None
    if not salary_range and description:
        salary_range = extract_salary(description)

    needs_review = get("needs_manual_review")
    needs_review = needs_review is True or str(needs_review).lower() == "true"

    views_count = get("views_count", 0)
    try:
        views_count = int(views_count)
    except (ValueError, TypeError):
        views_count = 0

    return {
        "id": stem,
        "organization_name": get("organization_name", "Unknown organization"),
        "organization_logo": get("organization_logo") or None,
        "title": get("title", "Untitled"),
        "description": description,
        "requirements": get("requirements") or None,
        "location": get("location") or None,
        "job_type": get("job_type", "full-time"),
        "salary_range": salary_range,
        "expires_at": get("expires_at") or None,
        "application_email": get("application_email") or None,
        "application_url": get("application_url") or None,
        "application_instructions": get("application_instructions") or None,
        "created_at": get("created_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "views_count": views_count,
        "added_by": get("added_by") or None,
        "needs_manual_review": needs_review,
    }


def md_to_seeker(file_path):
    post = frontmatter.load(str(file_path))
    fm = post.metadata
    body = (post.content or "").strip()
    stem = file_path.stem

    def get(k, default=""):
        v = fm.get(k)
        if v is None or v == "":
            return default
        return v

    return {
        "id": stem,
        "name": get("name", "Anonymous"),
        "headline": get("headline"),
        "location": get("location"),
        "skills": get("skills"),
        "experience_years": get("experience_years"),
        "experience_summary": get("experience_summary"),
        "profile_url": get("profile_url"),
        "availability": get("availability"),
        "github": get("github"),
        "linkedin": get("linkedin"),
        "portfolio": get("portfolio"),
        "email": get("email"),
        "twitter": get("twitter"),
        "resume_url": get("resume_url"),
        "created_at": get("created_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "about": body,
    }


def detect_duplicates(jobs):
    seen = {}
    duplicates = []
    for job in jobs:
        fingerprint = "|".join([
            (job["title"] or "").lower().strip(),
            (job["organization_name"] or "").lower().strip(),
            (job["location"] or "").lower().strip(),
        ])
        if fingerprint in seen:
            duplicates.append({
                "duplicate": job["id"],
                "original": seen[fingerprint],
                "fingerprint": fingerprint,
            })
        else:
            seen[fingerprint] = job["id"]
    return duplicates


def build_jobs():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not JOBS_DIR.exists():
        OUT_FILE.write_text(
            json.dumps(
                {"jobs": [], "count": 0, "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
                indent=2,
            ),
            encoding="utf-8",
        )
        return

    files = sorted(
        f for f in JOBS_DIR.iterdir() if f.suffix == ".md" and f.name != "README.md"
    )
    jobs = [md_to_job(f) for f in files]

    detect_duplicates(jobs)

    now = datetime.now(timezone.utc)
    active_jobs = []
    for job in jobs:
        if not job["expires_at"]:
            active_jobs.append(job)
            continue
        try:
            expiry = datetime.fromisoformat(job["expires_at"].replace("Z", "+00:00"))
            if expiry > now:
                active_jobs.append(job)
        except (ValueError, AttributeError):
            active_jobs.append(job)

    out = {
        "jobs": active_jobs,
        "count": len(active_jobs),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    OUT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")


def build_seekers():
    SEEKERS_OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not SEEKERS_DIR.exists():
        SEEKERS_OUT_FILE.write_text(
            json.dumps(
                {"seekers": [], "count": 0, "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
                indent=2,
            ),
            encoding="utf-8",
        )
        return

    files = sorted(
        f for f in SEEKERS_DIR.iterdir() if f.suffix == ".md" and f.name != "README.md"
    )
    seekers = [md_to_seeker(f) for f in files]
    out = {
        "seekers": seekers,
        "count": len(seekers),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    SEEKERS_OUT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")


def main():
    build_jobs()
    build_seekers()


if __name__ == "__main__":
    main()
