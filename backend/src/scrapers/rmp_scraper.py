from typing import Any
from datetime import datetime, timedelta, timezone
import os

import requests
import re
import json
import time

from langchain_core.documents import Document

RMP_REVIEW_LOOKBACK_YEARS = int(os.getenv("RMP_REVIEW_LOOKBACK_YEARS", "2"))
RMP_MAX_RECENT_REVIEWS = int(os.getenv("RMP_MAX_RECENT_REVIEWS", "1200"))
RMP_PROFESSOR_LOOKBACK_YEARS = int(os.getenv("RMP_PROFESSOR_LOOKBACK_YEARS", "2"))
RMP_TEACHER_ACTIVITY_PAGE_SIZE = int(os.getenv("RMP_TEACHER_ACTIVITY_PAGE_SIZE", "20"))
RMP_TEACHER_ACTIVITY_MAX_PAGES = int(os.getenv("RMP_TEACHER_ACTIVITY_MAX_PAGES", "3"))
RMP_VALIDATE_PROFESSOR_ACTIVITY = os.getenv("RMP_VALIDATE_PROFESSOR_ACTIVITY", "false").strip().lower() in {
    "1", "true", "yes", "on"
}


def _normalize_school_ql_id(raw_id: str) -> str:
    """
    RMP school IDs are base64-like relay IDs (e.g. U2Nob29sLTEwNzc=).
    If env/config drops trailing '=', pad to valid base64 length.
    """
    value = (raw_id or "").strip()
    if not value:
        return value
    padding = len(value) % 4
    if padding:
        value = value + ("=" * (4 - padding))
    return value


def _graphql_error_message(payload: dict[str, Any]) -> str | None:
    errors = payload.get("errors")
    if not errors:
        return None
    msgs = []
    for err in errors:
        if isinstance(err, dict):
            msg = err.get("message")
            if msg:
                msgs.append(str(msg))
    return "; ".join(msgs) if msgs else str(errors)


def _parse_review_date(raw_date: Any) -> datetime | None:
    if not raw_date:
        return None
    if not isinstance(raw_date, str):
        raw_date = str(raw_date)

    candidates = [raw_date]
    if raw_date.endswith("Z"):
        candidates.append(raw_date.replace("Z", "+00:00"))

    for candidate in candidates:
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except ValueError:
            continue
    return None


def get_school_reviews(school_ql_id: str) -> list:
    school_ql_id = _normalize_school_ql_id(school_ql_id)
    url = "https://www.ratemyprofessors.com/graphql"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": "Basic dGVzdDp0ZXN0",
        "Content-Type": "application/json"
    }

    query = """
    query SchoolRatingsListQuery($count: Int!, $id: ID!, $cursor: String) {
      node(id: $id) {
        __typename
        ... on School {
          ...SchoolRatingsList_school_1G22uz
        }
        id
      }
    }

    fragment SchoolRatingsList_school_1G22uz on School {
      id
      name
      city
      state
      country
      legacyId
      ratings(first: $count, after: $cursor) {
        edges {
          cursor
          node {
            ...SchoolRating_rating
            id
            __typename
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
      ...SchoolRating_school
    }

    fragment SchoolRating_rating on SchoolRating {
      clubsRating
      comment
      date
      facilitiesRating
      foodRating
      happinessRating
      internetRating
      locationRating
      opportunitiesRating
      reputationRating
      safetyRating
      socialRating
      legacyId
      flagStatus
      createdByUser
      ...SchoolRatingFooter_rating
    }

    fragment SchoolRatingFooter_rating on SchoolRating {
      id
      comment
      flagStatus
      legacyId
      ...Thumbs_schoolRating
    }

    fragment Thumbs_schoolRating on SchoolRating {
      id
      legacyId
      thumbsDownTotal
      thumbsUpTotal
      userThumbs {
        computerId
        thumbsUp
        thumbsDown
        id
      }
    }

    fragment SchoolRating_school on School {
      ...SchoolRatingSuperHeader_school
      ...SchoolRatingFooter_school
    }

    fragment SchoolRatingSuperHeader_school on School {
      name
      legacyId
    }

    fragment SchoolRatingFooter_school on School {
      id
      legacyId
      ...Thumbs_school
    }

    fragment Thumbs_school on School {
      id
      legacyId
    }
    """

    all_reviews = []
    cursor = ""
    has_next_page = True

    print(f"Starting review scrape for School ID: {school_ql_id}")

    while has_next_page:
        variables = {
            "count": 50,
            "id": school_ql_id,
            "cursor": cursor if cursor else ""
        }

        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

        if response.status_code != 200:
            print(f"Request failed with status {response.status_code}")
            break

        data = response.json()

        err_msg = _graphql_error_message(data)
        if err_msg:
            print(f"RMP review scrape GraphQL error: {err_msg}")
            break

        try:
            school_node = data["data"]["node"]
            if school_node is None:
                print("RMP review scrape returned null school node. Check UCSB_SCHOOL_ID format.")
                break
            ratings_data = school_node["ratings"]
            edges = ratings_data["edges"]
            page_info = ratings_data["pageInfo"]
        except (KeyError, TypeError) as e:
            print("Error parsing response structure:", e)
            print(json.dumps(data, indent=2))
            break

        for edge in edges:
            node = edge["node"]
            review_text = f"Date: {node.get('date')}\nReview: {node.get('comment')}"
            doc = Document(
                page_content=review_text,
                metadata={
                    "date": node.get("date"),
                    "source": "ratemyprofessors",
                }
            )
            all_reviews.append(doc)

        print(f"Fetched {len(edges)} reviews. Total: {len(all_reviews)}")

        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

        time.sleep(0.5)

    if not all_reviews:
        return all_reviews

    cutoff = datetime.utcnow() - timedelta(days=365 * RMP_REVIEW_LOOKBACK_YEARS)
    recent_reviews = []
    older_reviews = []
    undated_reviews = []

    for doc in all_reviews:
        dt = _parse_review_date(doc.metadata.get("date"))
        if dt is None:
            undated_reviews.append(doc)
            continue
        if dt >= cutoff:
            recent_reviews.append((dt, doc))
        else:
            older_reviews.append((dt, doc))

    recent_reviews.sort(key=lambda item: item[0], reverse=True)
    older_reviews.sort(key=lambda item: item[0], reverse=True)

    ordered_reviews = [doc for _, doc in recent_reviews] + [doc for _, doc in older_reviews] + undated_reviews

    if RMP_MAX_RECENT_REVIEWS > 0:
        ordered_reviews = ordered_reviews[:RMP_MAX_RECENT_REVIEWS]

    print(
        f"Prioritized recent reviews: {len(recent_reviews)} within {RMP_REVIEW_LOOKBACK_YEARS} years. "
        f"Returning {len(ordered_reviews)} total reviews."
    )

    return ordered_reviews


def get_school_ratings(school_id: str) -> Any:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }
    url = f"https://www.ratemyprofessors.com/school/{school_id}"
    page = requests.get(url=url, headers=headers)
    pattern = r'window\.__RELAY_STORE__\s*=\s*({.*?});'
    match = re.search(pattern, page.text, re.DOTALL)

    if match:
        json_str = match.group(1)
        data = json.loads(json_str)

        school_overall_rating = None
        school_amenities_rating = []

        for key, value in data.items():
            if isinstance(value, dict):
                if value.get("__typename") == "School":
                    if "avgRatingRounded" in value:
                        school_overall_rating = value["avgRatingRounded"]
                if value.get("__typename") == "SchoolSummary":
                    for amenity in list(value.keys())[2:]:
                        school_amenities_rating.append([amenity, value[amenity]])

        return school_overall_rating, school_amenities_rating
    return None


def get_school_professors(school_ql_id: str) -> list:
    school_ql_id = _normalize_school_ql_id(school_ql_id)
    url = "https://www.ratemyprofessors.com/graphql"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": "Basic dGVzdDp0ZXN0",
        "Content-Type": "application/json"
    }

    query = """
    query TeacherSearchPaginationQuery(
      $count: Int!
      $cursor: String
      $query: TeacherSearchQuery!
    ) {
      search: newSearch {
        ...TeacherSearchPagination_search_1jWD3d
      }
    }
    
    fragment CardFeedback_teacher on Teacher {
      wouldTakeAgainPercent
      avgDifficulty
    }
    
    fragment CardName_teacher on Teacher {
      firstName
      lastName
    }
    
    fragment CardSchool_teacher on Teacher {
      department
      school {
        name
        id
      }
    }
    
    fragment TeacherBookmark_teacher on Teacher {
      id
      isSaved
    }
    
    fragment TeacherCard_teacher on Teacher {
      id
      legacyId
      avgRating
      numRatings
      ...CardFeedback_teacher
      ...CardSchool_teacher
      ...CardName_teacher
      ...TeacherBookmark_teacher
    }
    
    fragment TeacherSearchPagination_search_1jWD3d on newSearch {
      teachers(query: $query, first: $count, after: $cursor) {
        didFallback
        edges {
          cursor
          node {
            ...TeacherCard_teacher
            id
            __typename
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
        resultCount
        filters {
          field
          options {
            value
            id
          }
        }
      }
    }
    """

    def get_teacher_recent_activity(teacher_id: str, cutoff_dt: datetime) -> tuple[bool, int, str | None]:
        """
        Returns:
          has_recent_review, recent_review_count, latest_review_date
        """
        teacher_query = """
        query TeacherRatingsActivityQuery($id: ID!, $count: Int!, $cursor: String) {
          node(id: $id) {
            __typename
            ... on Teacher {
              ratings(first: $count, after: $cursor) {
                edges {
                  node {
                    date
                  }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
              }
            }
            id
          }
        }
        """

        cursor_local = ""
        has_next_local = True
        pages_checked = 0
        recent_count = 0
        latest_dt = None

        while has_next_local and pages_checked < max(1, RMP_TEACHER_ACTIVITY_MAX_PAGES):
            variables_local = {
                "id": teacher_id,
                "count": max(1, RMP_TEACHER_ACTIVITY_PAGE_SIZE),
                "cursor": cursor_local if cursor_local else ""
            }

            try:
                response_local = requests.post(
                    url,
                    json={"query": teacher_query, "variables": variables_local},
                    headers=headers,
                    timeout=20,
                )
                if response_local.status_code != 200:
                    return False, 0, None
                payload_local = response_local.json()
                ratings_block = payload_local["data"]["node"]["ratings"]
                edges_local = ratings_block["edges"]
                page_info_local = ratings_block["pageInfo"]
            except Exception:
                return False, 0, None

            saw_older_review = False
            for edge_local in edges_local:
                raw_date = edge_local.get("node", {}).get("date")
                dt = _parse_review_date(raw_date)
                if dt is None:
                    continue

                if latest_dt is None or dt > latest_dt:
                    latest_dt = dt

                if dt >= cutoff_dt:
                    recent_count += 1
                else:
                    saw_older_review = True

            pages_checked += 1
            has_next_local = page_info_local.get("hasNextPage", False)
            cursor_local = page_info_local.get("endCursor")

            # Ratings are usually newest-first; once old dates appear, no need to keep paging.
            if saw_older_review:
                break

            time.sleep(0.15)

        latest_date_str = latest_dt.date().isoformat() if latest_dt else None
        return recent_count > 0, recent_count, latest_date_str

    all_professors = []
    cursor = ""
    has_next_page = True
    cutoff = datetime.utcnow() - timedelta(days=365 * RMP_PROFESSOR_LOOKBACK_YEARS)
    skipped_no_recent = 0

    print(f"Starting professor scrape for School ID: {school_ql_id}")
    if RMP_VALIDATE_PROFESSOR_ACTIVITY:
        print(f"Keeping professors with at least one review in last {RMP_PROFESSOR_LOOKBACK_YEARS} years.")
    else:
        print("Skipping per-professor review recency validation for faster scraping.")

    while has_next_page:
        variables = {
            "count": 50,
            "cursor": cursor if cursor else "",
            "query": {
                "text": "",
                "schoolID": school_ql_id
            }
        }

        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

        if response.status_code != 200:
            print(f"Request failed with status {response.status_code}")
            break

        data = response.json()

        err_msg = _graphql_error_message(data)
        if err_msg:
            print(f"RMP professor scrape GraphQL error: {err_msg}")
            break

        try:
            school_node = data["data"]["search"]
            if school_node is None or school_node.get("teachers") is None:
                print("RMP professor scrape returned null teachers. Check UCSB_SCHOOL_ID format.")
                break
            professor_data = school_node["teachers"]
            edges = professor_data["edges"]
            page_info = professor_data["pageInfo"]
        except (KeyError, TypeError) as e:
            print("Error parsing response structure:", e)
            print(json.dumps(data, indent=2))
            break

        for edge in edges:
            node = edge["node"]
            recent_count = None
            latest_review_date = None
            if RMP_VALIDATE_PROFESSOR_ACTIVITY:
                teacher_id = node.get("id")
                has_recent, recent_count, latest_review_date = get_teacher_recent_activity(teacher_id, cutoff)
                if not has_recent:
                    skipped_no_recent += 1
                    continue

            review_text = (
                f"Professor: {node.get('firstName')} {node.get('lastName')}\n"
                f"Rating: {node.get('avgRating')}\nDifficulty: {node.get('avgDifficulty')}\nWould_take_again"
                f"_percentage: {node.get('wouldTakeAgainPercent')}\nDepartment: {node.get('department')}"
            )
            doc = Document(
                page_content=review_text,
                metadata={
                    "Professor": f"{node.get('firstName')} {node.get('lastName')}",
                    "rating": node.get('avgRating'),
                    "difficulty": node.get('avgDifficulty'),
                    "would_take_again_percentage": node.get('wouldTakeAgainPercent'),
                    "department": node.get('department'),
                    "source": "ratemyprofessors",
                }
            )
            if RMP_VALIDATE_PROFESSOR_ACTIVITY:
                doc.metadata["recent_review_count"] = recent_count
                doc.metadata["latest_review_date"] = latest_review_date
                doc.metadata["lookback_years"] = RMP_PROFESSOR_LOOKBACK_YEARS
            all_professors.append(doc)

        if RMP_VALIDATE_PROFESSOR_ACTIVITY:
            print(
                f"Scanned {len(edges)} professors. "
                f"Kept: {len(all_professors)} | Skipped (no recent reviews): {skipped_no_recent}"
            )
        else:
            print(f"Scanned {len(edges)} professors. Total kept: {len(all_professors)}")

        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

        time.sleep(0.5)

    print(
        f"Professor scrape complete. Final kept professors: {len(all_professors)} "
        f"(lookback: {RMP_PROFESSOR_LOOKBACK_YEARS} years)"
    )
    return all_professors
