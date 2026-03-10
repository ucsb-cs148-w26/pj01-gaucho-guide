import backend.src.services.prereq_graph as pg


def test_build_remaining_graph_spec_filters_completed(tmp_path, monkeypatch):
    data_file = tmp_path / "prereqs.json"
    data_file.write_text(
        """
{
  "CMPSC 16": {"prereq_courses": ["MATH 3A"]},
  "CMPSC 24": {"prereq_courses": ["CMPSC 16", "MATH 3A"]},
  "CMPSC 32": {"prereq_courses": []}
}
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(pg, "DATA_PATH", data_file)

    nodes, edges = pg.build_remaining_graph_spec(["CMPSC 16"])

    assert "CMPSC 16" not in nodes
    assert "CMPSC 24" in nodes
    assert "CMPSC 32" in nodes
    assert ("CMPSC 16", "CMPSC 24") not in edges
    assert ("MATH 3A", "CMPSC 24") in edges


def test_extract_image_from_gemini_response_inline_data():
    payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Generated flowchart"},
                        {"inlineData": {"mimeType": "image/png", "data": "abc123"}},
                    ]
                }
            }
        ]
    }

    image_url = pg._extract_image_from_gemini_response(payload)
    assert image_url == "data:image/png;base64,abc123"


def test_generate_flowchart_image_with_gemini_returns_image(monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "inlineData": {
                                        "mimeType": "image/png",
                                        "data": "b64img",
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

    class FakeRequests:
        @staticmethod
        def post(url, json, timeout):
            captured["url"] = url
            captured["json"] = json
            captured["timeout"] = timeout
            return FakeResponse()

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("FLOWCHART_GEMINI_IMAGE_MODEL", "nano-banana-model")
    monkeypatch.setattr(pg, "requests", FakeRequests)

    image_url = pg.generate_flowchart_image_with_gemini("build me a graph")

    assert image_url == "data:image/png;base64,b64img"
    assert "nano-banana-model:generateContent" in captured["url"]
    assert "key=test-key" in captured["url"]
    assert captured["json"]["generationConfig"]["responseModalities"] == ["TEXT", "IMAGE"]


def test_generate_remaining_path_image_returns_none_when_done(monkeypatch):
    monkeypatch.setattr(pg, "build_remaining_graph_spec", lambda _: ([], []))

    image_url, message = pg.generate_remaining_path_image(["CMPSC 16"])

    assert image_url is None
    assert "completed all courses" in message.lower()

