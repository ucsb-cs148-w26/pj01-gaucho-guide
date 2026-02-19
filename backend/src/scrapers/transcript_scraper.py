"""
transcript_scraper.py
---------------------
Parses a UCSB unofficial transcript PDF into structured JSON using:
  1. pymupdf4llm  — converts the PDF to Markdown
  2. Pure Python regex — extracts structured data from the Markdown (no LLM, no API calls)

Output JSON schema
------------------
{
  "student_name":          str,
  "student_id":            str,
  "major":                 str,
  "courses": [
    {
      "quarter":       str,   # e.g. "Fall 2023"
      "course_code":   str,   # e.g. "CMPSC 16"
      "course_title":  str,
      "units":         float,
      "grade":         str | null,  # e.g. "A", "B+", "P", "NP", "W", "IP", null if in-progress
      "grade_points":  float | null
    }
  ],
  "cumulative_gpa":        float | null,
  "total_units_attempted": float | null,
  "total_units_passed":    float | null
}

Usage
-----
  from backend.src.scrapers.transcript_scraper import parse_transcript

  with open("transcript.pdf", "rb") as f:
      result = parse_transcript(f.read())
"""

import os
import re
import tempfile

import pymupdf4llm


def _pdf_to_markdown(pdf_bytes: bytes) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        tmp.write(pdf_bytes)
        tmp.close()
        return pymupdf4llm.to_markdown(tmp.name)
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


def _collapse_lines(md: str) -> str:
    """
    pymupdf4llm wraps long lines mid-word/mid-number.
    Join lines that are clearly continuations (no blank line separator,
    and the next line doesn't start a new logical block).
    We do this by collapsing the whole doc into a single long string,
    then re-splitting on double newlines (paragraph breaks).
    """
    paragraphs = re.split(r'\n{2,}', md)
    collapsed = []
    for para in paragraphs:
        # Join wrapped lines within a paragraph into one line
        single = " ".join(line.strip() for line in para.splitlines() if line.strip())
        collapsed.append(single)
    return "\n\n".join(collapsed)


def _parse_markdown(md: str) -> dict:
    text = _collapse_lines(md)
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # --- Student info ---
    student_name = None
    student_id = None
    major = None

    for line in lines:
        m = re.search(r'Perm(?:\s+Number)?[:\s]+([A-Z0-9]+)', line, re.IGNORECASE)
        if m:
            student_id = m.group(1)
            # Name is on the same collapsed line before "Perm"
            name_part = line[:m.start()].strip()
            name_clean = re.sub(r'[^A-Z\s\-]', '', name_part).strip()
            if name_clean:
                student_name = name_clean.title()
        m = re.search(r'(?:ENGR|L&S|COE|CLAS|BREN|EDUC|MUS|FINE)\s*/\s*(?:BS|BA|MS|PhD|Minor)\s*/\s*([A-Z]+)', line)
        if m:
            major = m.group(1).strip()

    # --- Patterns ---
    QUARTER_RE = re.compile(r'^(Fall|Winter|Spring|Summer)\s+((19|20)\d{2})$', re.IGNORECASE)
    GPA_VALUE_RE = re.compile(r'\*\*GPA\s+([\d.]+)\*\*')
    # Units block: att  comp  gpa  points  (4 floats in a row)
    UNITS_RE = re.compile(r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+([\d.]+)')

    # Strategy: anchor on 5-digit enrollment codes to split courses.
    # Each course chunk looks like:
    #   CODE -TITLE [**GRADE**] ENRLCD att comp gpa pts [SUBTITLE]
    # We find all enrollment code positions, then for each one work
    # backwards to find the course code+title and forwards for units.
    ENRL_RE = re.compile(r'\b(\d{5})\b')
    GRADE_RE = re.compile(r'\*\*([A-DF][+\-]?|P|NP|W|IP|S|U|I)\*\*')
    # Course code: 1-5 uppercase letters (dept), optional second word, then digits+suffix
    # e.g. CMPSC 16, PHYS 6AL, C LIT 30B, ES 1, BL ST 1, WRIT 105SW, PSTAT 120A
    COURSE_HEADER_RE = re.compile(
        r'([A-Z]{1,5}(?:\s[A-Z]{1,5})?\s*\d+[A-Z0-9]*(?:\s*-\s*\d+[A-Z]*)?)'
        r'\s*-\s*'
        r'([A-Z][A-Z0-9\s/&,\.\']*?)'
        r'\s*(?:\*\*[A-DF][+\-]?\*\*|\*\*[PW]\*\*|\*\*NP\*\*|\*\*IP\*\*|\d{5})'
    )
    # Subtitle: trailing ALL-CAPS word(s) after the units block, e.g. "SCI", "SOLVING I", "MICRO"
    SUBTITLE_RE = re.compile(r'[\d.]+\s+([A-Z][A-Z\s/&]*[A-Z])\s*$')

    courses = []
    current_quarter = None
    cumulative_gpa = None
    total_units_attempted = None
    total_units_passed = None

    for line in lines:
        # Skip page headers/footers
        if re.match(r'^https?://', line) or re.match(r'^\d{1,2}/\d{1,2}/\d{2,4}', line) or \
                "Printable Version" in line or "University of California" in line:
            continue

        # Quarter header (short line, just "Fall 2023" etc.)
        if QUARTER_RE.match(line):
            current_quarter = line.strip().title()
            continue

        # Cumulative total — keep updating so we end up with the final value
        if "Cumulative Total" in line:
            gpa_m = GPA_VALUE_RE.search(line)
            if gpa_m:
                cumulative_gpa = float(gpa_m.group(1))
            after_gpa = re.sub(r'.*\*\*GPA\s+[\d.]+\*\*', '', line)
            units_m = UNITS_RE.search(after_gpa)
            if units_m:
                total_units_attempted = float(units_m.group(1))
                total_units_passed = float(units_m.group(2))
            continue

        # Skip quarter totals, honors, transfer lines, table rows
        if any(tok in line for tok in (
            "Quarter Total", "Dean's Honors", "Transfer Work",
            "Att Course", "GradeEnrlCd", "|---|", "Institution Name",
        )):
            continue

        if not current_quarter:
            continue

        # Find all enrollment codes — each marks one course
        enrl_matches = list(ENRL_RE.finditer(line))
        if not enrl_matches:
            continue

        for idx, enrl_m in enumerate(enrl_matches):
            enrl_start = enrl_m.start()
            enrl_end = enrl_m.end()

            # The text before this enrollment code (back to previous enrl code or line start)
            prev_end = enrl_matches[idx - 1].end() if idx > 0 else 0
            before = line[prev_end:enrl_start].strip()

            # Parse course code and title from the "before" text
            ch_m = COURSE_HEADER_RE.search(before + " " + enrl_m.group())
            if not ch_m:
                # Fallback: try to find CODE -TITLE anywhere in before
                ch_m = re.search(
                    r'([A-Z]{1,4}(?:\s[A-Z]{1,4})?\s*\d+[A-Z0-9]*(?:\s*-\s*\d+[A-Z]*)?)'
                    r'\s*-\s*([A-Z][A-Z0-9\s/&,\.\']+)',
                    before
                )
            if not ch_m:
                continue

            course_code = ch_m.group(1).strip()
            course_title = ch_m.group(2).strip().title()

            # Grade is in the "before" text (between title and enrl code)
            grade_m = GRADE_RE.search(before)
            grade = grade_m.group(1) if grade_m else None

            # Units are after the enrollment code, up to next enrl code or end
            next_enrl_start = enrl_matches[idx + 1].start() if idx + 1 < len(enrl_matches) else len(line)
            after = line[enrl_end:next_enrl_start]
            units_m = UNITS_RE.search(after)
            if units_m:
                units = float(units_m.group(1))
                gp = float(units_m.group(4))
                grade_points = gp if gp > 0 else None
                # Subtitle word(s) appear after the units block on the same chunk
                after_units = after[units_m.end():]
                sub_m = re.match(r'\s+([A-Z][A-Z0-9\s/&]*?)(?:\s*$|\s+[A-Z]{1,5}\s*\d)', after_units)
                if sub_m:
                    subtitle = sub_m.group(1).strip().title()
                    if subtitle and subtitle.upper() not in ("UNDERGRAD", "HONORS"):
                        course_title = (course_title + " " + subtitle).strip()
            else:
                units = None
                grade_points = None

            courses.append({
                "quarter": current_quarter,
                "course_code": course_code,
                "course_title": course_title,
                "units": units,
                "grade": grade,
                "grade_points": grade_points,
            })

    return {
        "student_name": student_name,
        "student_id": student_id,
        "major": major,
        "courses": courses,
        "cumulative_gpa": cumulative_gpa,
        "total_units_attempted": total_units_attempted,
        "total_units_passed": total_units_passed,
    }


def parse_transcript(pdf_bytes: bytes) -> dict:
    markdown_text = _pdf_to_markdown(pdf_bytes)
    return _parse_markdown(markdown_text)
