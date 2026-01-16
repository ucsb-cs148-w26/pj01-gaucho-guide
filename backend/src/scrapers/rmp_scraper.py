from typing import Any

import requests
import re
import json
import time

from langchain_core.documents import Document


def get_school_reviews(school_ql_id: str) -> list:
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

        try:
            school_node = data["data"]["node"]
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

    return all_reviews


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

    all_professors = []
    cursor = ""
    has_next_page = True

    print(f"Starting professor scrape for School ID: {school_ql_id}")

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

        try:
            school_node = data["data"]["search"]
            professor_data = school_node["teachers"]
            edges = professor_data["edges"]
            page_info = professor_data["pageInfo"]
        except (KeyError, TypeError) as e:
            print("Error parsing response structure:", e)
            print(json.dumps(data, indent=2))
            break

        for edge in edges:
            node = edge["node"]
            review_text = (f"Professor: {node.get('firstName')} {node.get('lastName')}\n"
                           f"Rating: {node.get('avgRating')}\nDifficulty: {node.get('avgDifficulty')}\nWould_take_again"
                           f"_percentage: {node.get('wouldTakeAgainPercent')}\nDepartment: {node.get('department')}")
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
            all_professors.append(doc)

        print(f"Fetched {len(edges)} professors. Total: {len(all_professors)}")

        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]

        time.sleep(0.5)

    return all_professors
