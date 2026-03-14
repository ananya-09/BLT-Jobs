#!/usr/bin/env python3
"""
Parse GitHub issue form body (### Label\n\nvalue) and write jobs/<slug>.md
with YAML frontmatter. Used by process-submissions.yml for [JOB] form issues.
Reads issue body from stdin or first argument.
"""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent.parent / "jobs"


def parse_form_body(body):
    data = {}
    sections = re.split(r"\n### ", body)
    for section in filter(None, sections):
        newline_pos = section.find("\n")
        if newline_pos == -1:
            label = section.strip()
            value = ""
        else:
            label = section[:newline_pos].strip()
            value = section[newline_pos:]

        # Remove optional marker
        label = re.sub(r"\s*\(Optional\)\s*$", "", label)
        label = re.sub(r"^#+\s*", "", label).strip()

        # Trim leading newlines, stop at next section
        value = re.sub(r"^\n+", "", value)
        value = re.split(r"\n\n###", value)[0].strip()

        data[label] = value
    return data


def slugify(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    s = s.strip("-")
    return s or "job"


def escape_yaml_value(v):
    return str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def main():
    if len(sys.argv) > 1:
        body = sys.argv[1]
    else:
        body = sys.stdin.read()

    d = parse_form_body(body)

    company = (d.get("Company Name") or d.get("Company") or "").strip()
    title = (d.get("Job Title") or d.get("Title") or "Untitled").strip()
    location = (d.get("Location") or "").strip()
    job_type = (d.get("Job Type") or "Full-time").strip().lower().replace(" ", "-")
    salary_range = (d.get("Salary Range") or d.get("Salary") or "").strip()
    description = (d.get("Job Description") or d.get("Description") or "").strip()
    requirements = (d.get("Requirements") or "").strip()
    how_to_apply = (d.get("How to Apply") or "").strip()
    website = (d.get("Company Website") or d.get("Website") or "").strip()
    additional_info = (d.get("Additional Information") or "").strip()

    org_slug = slugify(company) or "company"
    title_slug = slugify(title)[:50] or "job"
    filename = f"{org_slug}-{title_slug}.md"
    out_path = JOBS_DIR / filename
    n = 0
    while out_path.exists():
        n += 1
        out_path = JOBS_DIR / f"{org_slug}-{title_slug}-{n}.md"

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    added_by = os.environ.get("ISSUE_USER", "").strip()
    application_url = website or ""

    body_parts = [description]
    if requirements:
        body_parts.append(f"## Requirements\n\n{requirements}")
    if how_to_apply:
        body_parts.append(f"## How to Apply\n\n{how_to_apply}")
    if additional_info:
        body_parts.append(f"## Additional Information\n\n{additional_info}")
    description_body = "\n\n".join(filter(None, body_parts))

    frontmatter = {
        "title": title or "Untitled",
        "organization_name": company or "Company",
        "organization_logo": "",
        "location": location,
        "job_type": job_type or "full-time",
        "salary_range": salary_range,
        "expires_at": "",
        "application_email": "",
        "application_url": application_url,
        "application_instructions": how_to_apply,
        "requirements": requirements,
        "created_at": created,
        "views_count": 0,
        "added_by": added_by,
        "needs_manual_review": False,
    }

    lines = ["---"]
    for k, v in frontmatter.items():
        lines.append(f'{k}: "{escape_yaml_value(v)}"')
    lines += ["---", "", description_body]

    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")

    # Print relative path from cwd
    try:
        print(str(out_path.relative_to(Path.cwd())))
    except ValueError:
        print(str(out_path))


if __name__ == "__main__":
    main()
