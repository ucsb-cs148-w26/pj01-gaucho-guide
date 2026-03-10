from backend.src.services.professor_json_lookup import (
    format_professor_matches_for_context,
    search_local_professors,
)


def test_search_local_professors_exact_name_match(tmp_path):
    file_path = tmp_path / "ucsb_professors.json"
    file_path.write_text(
        """
{
  "professors": [
    {
      "name": "Jane Doe",
      "department": "Computer Science",
      "quality_rating": 4.7,
      "num_ratings": 25,
      "would_take_again_pct": 88,
      "difficulty_level": 2.9,
      "profile_url": "https://example.com/jane",
      "comments": ["Great lecturer"]
    },
    {
      "name": "John Smith",
      "department": "Mathematics",
      "quality_rating": 3.9,
      "num_ratings": 11,
      "would_take_again_pct": 70,
      "difficulty_level": 3.4,
      "profile_url": "https://example.com/john",
      "comments": []
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    matches = search_local_professors("Tell me about Professor Jane Doe", path=str(file_path))

    assert matches
    assert matches[0]["name"] == "Jane Doe"


def test_search_local_professors_followup_expanded_query(tmp_path):
    file_path = tmp_path / "ucsb_professors.json"
    file_path.write_text(
        """
{
  "professors": [
    {
      "name": "Jane Doe",
      "department": "Computer Science",
      "quality_rating": 4.7,
      "num_ratings": 25,
      "would_take_again_pct": 88,
      "difficulty_level": 2.9,
      "profile_url": "https://example.com/jane",
      "comments": ["Great lecturer"]
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    expanded_query = "Tell me about Professor Jane Doe\nFollow-up: what about her"
    matches = search_local_professors(expanded_query, path=str(file_path))

    assert matches
    assert matches[0]["name"] == "Jane Doe"


def test_search_local_professors_nickname_alias(tmp_path):
    file_path = tmp_path / "ucsb_professors.json"
    file_path.write_text(
        """
{
  "professors": [
    {
      "name": "Phillip Christopher",
      "department": "Chemical Engineering",
      "quality_rating": 4.3,
      "num_ratings": 10,
      "would_take_again_pct": 82,
      "difficulty_level": 3.2
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    matches = search_local_professors("Can you tell me about Professor Phill Christopher?", path=str(file_path))

    assert matches
    assert matches[0]["name"] == "Phillip Christopher"


def test_search_local_professors_department_hint(tmp_path):
    file_path = tmp_path / "ucsb_professors.json"
    file_path.write_text(
        """
{
  "professors": [
    {
      "name": "Kate Person",
      "department": "Computer Science",
      "quality_rating": 4.1,
      "num_ratings": 8,
      "would_take_again_pct": 77,
      "difficulty_level": 3.0
    },
    {
      "name": "Kate Person",
      "department": "Mathematics",
      "quality_rating": 3.8,
      "num_ratings": 11,
      "would_take_again_pct": 68,
      "difficulty_level": 3.4
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    matches = search_local_professors("Professor Kate in CMPSC", path=str(file_path))

    assert matches
    assert matches[0]["department"] == "Computer Science"


def test_format_professor_matches_for_context_contains_expected_fields():
    text = format_professor_matches_for_context(
        [
            {
                "name": "Jane Doe",
                "department": "Computer Science",
                "quality_rating": 4.7,
                "num_ratings": 25,
                "would_take_again_pct": 88,
                "difficulty_level": 2.9,
                "profile_url": "https://example.com/jane",
                "comments": ["Great lecturer"],
            }
        ]
    )

    assert "Professor: Jane Doe" in text
    assert "Profile URL: https://example.com/jane" in text
