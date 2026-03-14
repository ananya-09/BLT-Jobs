#!/usr/bin/env python3
"""
Parse GitHub issue body (markdown **Label:** value or ### Label\n\nvalue)
and write seekers/<slug>.md. Used by process-submissions.yml for [SEEKER] issues.
Reads issue body from stdin or first argument.
"""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SEEKERS_DIR = Path(__file__).resolve().parent.parent / "seekers"


def parse_form_body(body):
    data = {}

    # Extract **Label:** value pairs (inline within sections)
    bold_regex = re.compile(r"\*\*([^*]+):\*\*\s*([^\n]+)")
    for m in bold_regex.finditer(body):
        data[m.group(1).strip()] = m.group(2).strip()

    # Extract ## Section content (for multi-line sections)
    section_regex = re.compile(r"## ([^\n]+)\n((?:(?!## ).|\n)*)", re.DOTALL)
    for m in section_regex.finditer(body):
        label = m.group(1).strip()
        label = re.sub(r"\s*\(Optional\)\s*$", "", label)
        value = m.group(2).strip()
        # Skip if section only contains **Label:** pairs (already extracted)
        if not re.match(r"^\*\*[^*]+:\*\*", value):
            if label not in data:
                data[label] = value

    return data


def slugify(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    s = s.strip("-")
    return s or "seeker"


def extract_links(data):
    def clean(val):
        return re.sub(r"^[(\s]+|[)\s]+$", "", (val or "").strip())

    return {
        "github": clean(data.get("GitHub", "")),
        "linkedin": clean(data.get("LinkedIn", "")),
        "portfolio": clean(data.get("Portfolio/Website", "")),
        "email": clean(data.get("Email", "")),
        "twitter": clean(data.get("Twitter/X", "")),
        "resume": clean(data.get("Resume", "")),
    }


def escape_yaml_value(v):
    return str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def main():
    if len(sys.argv) > 1:
        body = sys.argv[1]
    else:
        body = sys.stdin.read()

    d = parse_form_body(body)

    name = (d.get("Name") or "").strip() or "Anonymous"
    headline = (d.get("Current Title/Role") or d.get("Title") or d.get("Headline") or "").strip()
    location = (d.get("Location") or "").strip()
    skills = (d.get("Skills") or "").strip()
    experience = (d.get("Years of Experience") or "").strip()
    availability = (d.get("Availability") or d.get("Preferred Job Type") or "").strip()
    about = (d.get("About Me") or "").strip()
    work_experience = (d.get("Work Experience") or d.get("Experience Highlights") or "").strip()
    projects = (d.get("Projects & Portfolio") or "").strip()
    certifications = (d.get("Certifications & Education") or "").strip()
    work_samples = (d.get("Work Samples") or "").strip()
    looking_for = (d.get("What I'm Looking For") or "").strip()

    links = extract_links(d)
    experience_summary = f"{experience} years" if experience else ""

    filename = f"{slugify(name)}.md"
    out_path = SEEKERS_DIR / filename
    n = 0
    while out_path.exists():
        n += 1
        out_path = SEEKERS_DIR / f"{slugify(name)}-{n}.md"

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    frontmatter_data = {
        "name": name or "Anonymous",
        "headline": headline,
        "location": location,
        "skills": skills,
        "experience_years": experience,
        "experience_summary": experience_summary,
        "availability": availability,
        "github": links["github"],
        "linkedin": links["linkedin"],
        "portfolio": links["portfolio"],
        "email": links["email"],
        "twitter": links["twitter"],
        "resume_url": links["resume"],
        "created_at": created,
    }

    body_parts = []
    if about:
        body_parts.append(f"## About Me\n\n{about}")
    if work_experience:
        body_parts.append(f"## Work Experience\n\n{work_experience}")
    if projects:
        body_parts.append(f"## Projects & Portfolio\n\n{projects}")
    if certifications:
        body_parts.append(f"## Certifications & Education\n\n{certifications}")
    if work_samples:
        body_parts.append(f"## Work Samples\n\n{work_samples}")
    if looking_for:
        body_parts.append(f"## What I'm Looking For\n\n{looking_for}")
    body_content = "\n\n".join(body_parts) or "Profile created via issue."

    lines = ["---"]
    for k, v in frontmatter_data.items():
        lines.append(f'{k}: "{escape_yaml_value(v)}"')
    lines += ["---", "", body_content]

    SEEKERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            try:
                f.write(f"path={out_path.relative_to(Path.cwd())}\n")
            except ValueError:
                f.write(f"path={out_path}\n")


if __name__ == "__main__":
    main()
