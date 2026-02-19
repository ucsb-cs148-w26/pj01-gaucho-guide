import os
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import requests
from langchain_core.documents import Document

DEFAULT_SUBREDDITS = tuple(
    s.strip()
    for s in os.getenv("REDDIT_CLASS_SUBREDDITS", "UCSantaBarbara,SantaBarbara").split(",")
    if s.strip()
)
DEFAULT_LIMIT = int(os.getenv("REDDIT_CLASS_LIMIT", "25"))
DEFAULT_MIN_SCORE = int(os.getenv("REDDIT_CLASS_MIN_SCORE", "0"))
DEFAULT_MIN_COMMENTS = int(os.getenv("REDDIT_CLASS_MIN_COMMENTS", "0"))
CMPSC_DISCOVERY_QUERY = os.getenv("REDDIT_CMPSC_DISCOVERY_QUERY", "CMPSC")
CMPSC_DISCOVERY_LIMIT = int(os.getenv("REDDIT_CMPSC_DISCOVERY_LIMIT", "300"))
CMPSC_MAX_COURSES = int(os.getenv("REDDIT_CMPSC_MAX_COURSES", "80"))
CMPSC_PER_COURSE_LIMIT = int(os.getenv("REDDIT_CMPSC_PER_COURSE_LIMIT", "30"))
CMPSC_SEED_CODES = [
    c.strip().upper()
    for c in os.getenv(
        "REDDIT_CMPSC_SEED_CODES",
        "CMPSC 8,CMPSC 9,CMPSC 16,CMPSC 24,CMPSC 32,CMPSC 40,CMPSC 64,CMPSC 111,CMPSC 120,CMPSC 130A,CMPSC 130B,CMPSC 138,CMPSC 156,CMPSC 160,CMPSC 170,CMPSC 176A",
    ).split(",")
    if c.strip()
]


def extract_course_codes(text: str) -> list[str]:
    """
    Extract likely course codes from user text.
    Examples: CMPSC 130A, PSTAT120A, ECON 10A, C LIT 30A.
    """
    if not text:
        return []

    pattern = re.compile(r"\b([A-Za-z]{1,5}(?:\s+[A-Za-z]{1,5})?)\s*([0-9]{1,3}[A-Za-z]{0,2})\b")
    codes: list[str] = []
    for dept, number in pattern.findall(text):
        dept_clean = " ".join(part.upper() for part in dept.strip().split())
        if len(dept_clean.replace(" ", "")) < 2:
            continue
        code = f"{dept_clean} {number.upper()}".strip()
        if code not in codes:
            codes.append(code)
    return codes


def _build_doc_text(item: dict[str, Any]) -> str:
    parts = []
    parts.append(f"Source: Reddit r/{item.get('subreddit', '')}")
    parts.append(f"Query: {item.get('query', '')}")
    parts.append(f"Course code: {item.get('course_code', '')}")
    parts.append(f"Title: {item.get('title', '')}".strip())

    flair = item.get("link_flair_text") or ""
    if flair:
        parts.append(f"Flair: {flair}")

    selftext = (item.get("selftext") or "").strip()
    if selftext:
        parts.append("Post:")
        parts.append(selftext)

    created = item.get("created_iso") or ""
    if created:
        parts.append(f"Created: {created}")

    parts.append(f"Score: {item.get('score')}, Comments: {item.get('num_comments')}")
    parts.append(f"Permalink: {item.get('permalink', '')}")
    return "\n".join(parts).strip()


def fetch_reddit_docs_for_course(
    course_code: str,
    subreddits: list[str] | None = None,
    limit: int = DEFAULT_LIMIT,
    min_score: int = DEFAULT_MIN_SCORE,
    min_comments: int = DEFAULT_MIN_COMMENTS,
) -> list[Document]:
    """
    Search Reddit JSON endpoints and return RAG-ready LangChain Documents.
    """
    if not course_code:
        return []

    active_subreddits = subreddits or list(DEFAULT_SUBREDDITS)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json,text/plain,*/*",
    }

    docs: list[Document] = []
    seen_post_ids: set[str] = set()

    for subreddit in active_subreddits:
        params = {
            "q": course_code,
            "restrict_sr": 1,
            "sort": "new",
            "t": "all",
            "limit": max(1, min(100, int(limit))),
            "raw_json": 1,
        }
        url = f"https://www.reddit.com/r/{subreddit}/search.json?{urlencode(params)}"

        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                continue
            payload = response.json()
            children = ((payload.get("data") or {}).get("children") or [])
        except Exception:
            continue

        for child in children:
            post = child.get("data") or {}
            post_id = post.get("id")
            if not post_id or post_id in seen_post_ids:
                continue
            seen_post_ids.add(post_id)

            if bool(post.get("over_18")):
                continue

            score = int(post.get("score") or 0)
            num_comments = int(post.get("num_comments") or 0)
            if score < min_score and num_comments < min_comments:
                continue

            created_utc = post.get("created_utc")
            created_iso = ""
            if created_utc:
                try:
                    created_iso = datetime.fromtimestamp(float(created_utc), tz=timezone.utc).isoformat()
                except Exception:
                    created_iso = ""

            permalink = post.get("permalink") or ""
            full_permalink = f"https://www.reddit.com{permalink}" if permalink else ""

            item = {
                "query": course_code,
                "course_code": course_code,
                "subreddit": subreddit,
                "post_id": post_id,
                "title": post.get("title") or "",
                "selftext": post.get("selftext") or "",
                "permalink": full_permalink,
                "score": score,
                "num_comments": num_comments,
                "created_iso": created_iso,
                "link_flair_text": post.get("link_flair_text") or "",
                "author": post.get("author") or "",
            }

            docs.append(
                Document(
                    page_content=_build_doc_text(item),
                    metadata={
                        "source": "reddit",
                        "subreddit": subreddit,
                        "course_code": course_code,
                        "post_id": post_id,
                        "permalink": full_permalink,
                        "score": score,
                        "num_comments": num_comments,
                        "created_iso": created_iso,
                        "author": item["author"],
                    },
                )
            )

    return docs


def _search_posts(
    query: str,
    subreddit: str,
    limit: int,
    sort: str = "new",
    min_score: int = DEFAULT_MIN_SCORE,
    min_comments: int = DEFAULT_MIN_COMMENTS,
) -> list[dict[str, Any]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json,text/plain,*/*",
    }

    results: list[dict[str, Any]] = []
    after = None
    target = max(1, limit)

    while len(results) < target:
        page_size = min(100, target - len(results))
        params = {
            "q": query,
            "restrict_sr": 1,
            "sort": sort,
            "t": "all",
            "limit": page_size,
            "raw_json": 1,
        }
        if after:
            params["after"] = after
        url = f"https://www.reddit.com/r/{subreddit}/search.json?{urlencode(params)}"

        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                break
            payload = response.json()
            data = payload.get("data") or {}
            children = data.get("children") or []
            after = data.get("after")
        except Exception:
            break

        if not children:
            break

        for child in children:
            post = child.get("data") or {}
            if bool(post.get("over_18")):
                continue
            score = int(post.get("score") or 0)
            num_comments = int(post.get("num_comments") or 0)
            if score < min_score and num_comments < min_comments:
                continue
            results.append(post)
            if len(results) >= target:
                break

        if not after:
            break

    return results


def discover_cmpsc_course_codes(
    subreddits: list[str] | None = None,
    discovery_limit: int = CMPSC_DISCOVERY_LIMIT,
) -> list[str]:
    active_subreddits = subreddits or list(DEFAULT_SUBREDDITS)
    discovered: set[str] = set(CMPSC_SEED_CODES)

    for subreddit in active_subreddits:
        posts = _search_posts(
            query=CMPSC_DISCOVERY_QUERY,
            subreddit=subreddit,
            limit=max(1, discovery_limit),
            sort="new",
        )

        for post in posts:
            title = post.get("title") or ""
            selftext = post.get("selftext") or ""
            combined = f"{title}\n{selftext}"
            codes = extract_course_codes(combined)
            for code in codes:
                if code.startswith("CMPSC "):
                    discovered.add(code)

    # Sort by course number when possible (e.g., CMPSC 130A)
    def _sort_key(code: str):
        m = re.search(r"CMPSC\s+(\d+)([A-Z]*)", code)
        if not m:
            return (9999, code)
        return (int(m.group(1)), m.group(2), code)

    return sorted(discovered, key=_sort_key)


def fetch_reddit_docs_for_cmpsc_catalog(
    subreddits: list[str] | None = None,
    max_courses: int = CMPSC_MAX_COURSES,
    per_course_limit: int = CMPSC_PER_COURSE_LIMIT,
    min_score: int = DEFAULT_MIN_SCORE,
    min_comments: int = DEFAULT_MIN_COMMENTS,
) -> tuple[list[Document], list[str]]:
    """
    Broad CMPSC Reddit harvest:
    1) discover many CMPSC course codes from Reddit posts
    2) query each code and gather docs
    3) dedupe by post_id
    Returns (docs, course_codes_used).
    """
    codes = discover_cmpsc_course_codes(subreddits=subreddits)
    if max_courses > 0:
        codes = codes[:max_courses]

    all_docs: list[Document] = []
    seen_post_ids: set[str] = set()

    for code in codes:
        docs = fetch_reddit_docs_for_course(
            course_code=code,
            subreddits=subreddits,
            limit=per_course_limit,
            min_score=min_score,
            min_comments=min_comments,
        )
        for doc in docs:
            post_id = str(doc.metadata.get("post_id", ""))
            if not post_id or post_id in seen_post_ids:
                continue
            seen_post_ids.add(post_id)
            all_docs.append(doc)

    return all_docs, codes
