#!/usr/bin/env python3
"""
Salary extraction utility for job descriptions.
Extracts and normalizes salary information from job description text.
"""

import re
import sys


def extract_salary(text):
    """
    Extract salary information from text.
    Returns a normalized salary range string or None.
    """
    if not text:
        return None

    # Common salary patterns
    patterns = [
        # $100,000 - $150,000 or $100k - $150k
        r"\$\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*[-\u2013\u2014]\s*\$?\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*(USD|CAD|EUR|GBP|per year|/year|annually)?",
        # $100,000 to $150,000
        r"\$\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s+to\s+\$?\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*(USD|CAD|EUR|GBP|per year|/year|annually)?",
        # Annual Salary: $100,000 — $150,000
        r"(?:annual|base|total)?\s*(?:salary|compensation|pay):\s*\$\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*[-\u2013\u2014]\s*\$?\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*(USD|CAD|EUR|GBP)?",
        # Hiring Ranges: $100,000 — $150,000
        r"hiring\s+ranges?:\s*[^\$]*\$\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*[-\u2013\u2014]\s*\$?\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*(USD|CAD|EUR|GBP)?",
        # £50,000 - £70,000 or €60,000 - €80,000
        r"([£€])\s*(\d{1,3}(?:,\d{3})*|\d+)k?\s*[-\u2013\u2014]\s*\1?\s*(\d{1,3}(?:,\d{3})*|\d+)k?",
    ]

    matches = []
    for pattern in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matches.append(m)

    if not matches:
        return None

    match = matches[0]
    matched_str = match.group(0)

    if "£" in matched_str:
        currency = "GBP"
        min_val = match.group(2)
        max_val = match.group(3)
    elif "€" in matched_str:
        currency = "EUR"
        min_val = match.group(2)
        max_val = match.group(3)
    else:
        min_val = match.group(1)
        max_val = match.group(2)
        raw_currency = (match.group(3) or "USD").upper()
        currency = re.sub(r"[^A-Z]", "", raw_currency)

    if currency not in ("USD", "CAD", "EUR", "GBP"):
        currency = "USD"

    def normalize_number(num):
        num = num.replace(",", "")
        if "k" in matched_str.lower() and int(num) < 1000:
            return int(num) * 1000
        return int(num)

    min_salary = normalize_number(min_val)
    max_salary = normalize_number(max_val)

    currency_symbol = {"USD": "$", "CAD": "CAD $", "EUR": "€", "GBP": "£"}.get(
        currency, "$"
    )

    return f"{currency_symbol}{min_salary:,} - {currency_symbol}{max_salary:,}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: extract_salary.py "<job description text>"', file=sys.stderr)
        sys.exit(1)
    result = extract_salary(sys.argv[1])
    print(result or "No salary found")
