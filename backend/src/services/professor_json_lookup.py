import json
import os
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path


DEFAULT_JSON_PATH = Path(__file__).resolve().parents[3] / "ucsb_professors.json"
STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "for",
    "her",
    "him",
    "i",
    "in",
    "is",
    "me",
    "of",
    "on",
    "prof",
    "professor",
    "tell",
    "that",
    "the",
    "them",
    "this",
    "to",
    "what",
    "who",
    "cmpsc",
    "cs",
    "econ",
    "math",
    "pstat",
    "phys",
    "engr",
}
TOKEN_ALIASES = {
    "phill": "phil",
    "philip": "phil",
    "phillip": "phil",
    "phillippe": "phil",
    "katie": "kate",
}
DEPARTMENT_HINTS = {
    "cmpsc": "computer science",
    "cs": "computer science",
    "comp sci": "computer science",
    "computer science": "computer science",
    "c e": "computer engineering",
    "ce": "computer engineering",
    "econ": "economics",
    "math": "mathematics",
    "pstat": "statistics",
}


def _normalize_text(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def _canonicalize_token(token: str) -> str:
    return TOKEN_ALIASES.get(token, token)


def _query_terms(query: str) -> list[str]:
    terms = []
    for token in _normalize_text(query).split():
        token = _canonicalize_token(token)
        if token in STOP_WORDS:
            continue
        if token.isdigit():
            continue
        if len(token) < 2:
            continue
        terms.append(token)
    return terms


def _department_hint(query: str) -> str | None:
    q = _normalize_text(query)
    for key, value in DEPARTMENT_HINTS.items():
        if key in q:
            return value
    return None


@lru_cache(maxsize=4)
def _load_records_cached(resolved_path: str) -> tuple[dict, ...]:
    path = Path(resolved_path)
    if not path.exists():
        return tuple()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return tuple()

    rows = payload.get("professors", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        return tuple()

    clean_rows = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        if not name:
            continue
        clean_rows.append(row)
    return tuple(clean_rows)


def load_local_professor_records(path: str | None = None) -> list[dict]:
    raw_path = path or os.getenv("UCSB_PROFESSORS_JSON_PATH") or str(DEFAULT_JSON_PATH)
    resolved = str(Path(raw_path).expanduser().resolve())
    return list(_load_records_cached(resolved))


def _score_match(name: str, query: str) -> int:
    name_norm = _normalize_text(name)
    query_norm = _normalize_text(query)
    if not name_norm or not query_norm:
        return 0

    score = 0
    name_terms = {_canonicalize_token(tok) for tok in name_norm.split()}
    query_terms = set(_query_terms(query_norm))
    overlap = len(name_terms & query_terms)

    if name_norm in query_norm:
        score += 1000
    if query_norm in name_norm and len(query_norm) >= 4:
        score += 250
    if overlap:
        score += overlap * 180
        if overlap == len(name_terms):
            score += 220

    ratio = SequenceMatcher(None, query_norm, name_norm).ratio()
    score += int(ratio * 80)

    # Avoid loose first-name-only collisions for two-token queries
    # like "Phill Conrad" matching "Phillip Christopher".
    if len(query_terms) >= 2 and overlap < 2 and ratio < 0.62:
        return 0

    if score < 120:
        return 0
    return score


def search_local_professors(query: str, limit: int = 4, path: str | None = None) -> list[dict]:
    records = load_local_professor_records(path)
    if not query or not records:
        return []

    ranked = []
    for row in records:
        score = _score_match(str(row.get("name", "")), query)
        if score <= 0:
            continue
        ranked.append((score, row))

    dept_hint = _department_hint(query)
    if dept_hint:
        dept_ranked = []
        for score, row in ranked:
            department = _normalize_text(str(row.get("department", "")))
            if dept_hint in department:
                dept_ranked.append((score + 80, row))
        if dept_ranked:
            ranked = dept_ranked

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in ranked[:limit]]


def format_professor_matches_for_context(matches: list[dict]) -> str:
    if not matches:
        return "No matching professor profile found."

    chunks = []
    for row in matches:
        name = str(row.get("name", "")).strip() or "Unknown"
        department = str(row.get("department", "")).strip() or "Unknown"
        quality = row.get("quality_rating")
        difficulty = row.get("difficulty_level")
        num_ratings = row.get("num_ratings")
        would_take_again = row.get("would_take_again_pct")
        profile_url = str(row.get("profile_url", "")).strip() or "N/A"
        comments = row.get("comments", [])
        if not isinstance(comments, list):
            comments = []
        comment_preview = " | ".join(str(c).strip() for c in comments if str(c).strip())
        if not comment_preview:
            comment_preview = "No comments available."

        chunks.append(
            "\n".join(
                [
                    f"Professor: {name}",
                    f"Department: {department}",
                    f"Quality Rating: {quality}",
                    f"Difficulty: {difficulty}",
                    f"Number of Ratings: {num_ratings}",
                    f"Would Take Again (%): {would_take_again}",
                    f"Profile URL: {profile_url}",
                    f"Comments: {comment_preview}",
                ]
            )
        )

    return "\n\n".join(chunks)
