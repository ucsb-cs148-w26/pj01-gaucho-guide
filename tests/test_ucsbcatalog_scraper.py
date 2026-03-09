import unittest
from unittest.mock import patch, MagicMock
from backend.src.scrapers.ucsbcatalog_scraper import UCSBCatalogClient


class TestUCSBCatalogClient(unittest.TestCase):

    @patch('os.getenv')
    def setUp(self, mock_getenv):
        mock_getenv.return_value = "dummy_api_key_123"
        self.client = UCSBCatalogClient()

    @patch('os.getenv')
    def test_init_missing_api_key(self, mock_getenv):
        mock_getenv.return_value = None
        with self.assertRaises(ValueError) as context:
            UCSBCatalogClient()
        self.assertIn("UCSB_API_KEY not found", str(context.exception))

    def test_format_class_data(self):
        # Test the pure formatting logic with a dummy class payload
        mock_course = {
            "courseId": "CMPSC 8",
            "title": "INTRO TO COMP SCI",
            "quarter": "20241",
            "description": "Introduction to computer science.",
            "college": "ENGR",
            "unitsFixed": 4,
            "classSections": [
                {
                    "enrollCode": "12345",
                    "section": "0100",
                    "enrolledTotal": 45,
                    "maxEnroll": 50,
                    "instructors": [{"instructor": "SMITH J"}],
                    "timeLocations": [
                        {
                            "days": "T R",
                            "beginTime": "14:00",
                            "endTime": "15:15",
                            "building": "PHELP",
                            "room": "3515"
                        }
                    ]
                }
            ]
        }

        formatted = self.client._format_class_data(mock_course)

        # Verify essential information is in the formatted RAG string
        self.assertIn("Course: CMPSC 8 - INTRO TO COMP SCI (20241)", formatted)
        self.assertIn("College: ENGR | Units: 4", formatted)
        self.assertIn("Description: Introduction to computer science.", formatted)
        self.assertIn("Section: 0100 (Code: 12345)", formatted)
        self.assertIn("Instructor(s): SMITH J", formatted)
        self.assertIn("T R 14:00-15:15 at PHELP 3515", formatted)
        self.assertIn("Capacity: 45/50 Enrolled", formatted)

    @patch('requests.Session.get')
    def test_get_class_by_enrollcode_success(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "courseId": "MATH 3A",
            "title": "CALCULUS I",
            "quarter": "20241"
        }
        mock_get.return_value = mock_response

        # Execute
        result = self.client.get_class_by_enrollcode("20241", "54321")

        # Assert
        mock_get.assert_called_once_with("https://api.ucsb.edu/academics/curriculums/v3/classes/20241/54321")
        self.assertIn("MATH 3A", result)
        self.assertIn("CALCULUS I", result)

    @patch('requests.Session.get')
    def test_get_class_by_enrollcode_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        result = self.client.get_class_by_enrollcode("20241", "99999")

        self.assertEqual(result, "Failed to fetch class. Status: 404, Response: Not Found")

    @patch('requests.Session.get')
    def test_search_classes(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "classes": [
                {"courseId": "PHYS 1", "title": "PHYSICS 1"},
                {"courseId": "PHYS 2", "title": "PHYSICS 2"}
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.search_classes({"subjectCode": "PHYS"})

        self.assertIn("PHYS 1", result)
        self.assertIn("PHYS 2", result)
        self.assertIn("---", result)  # Checks for our separator

    @patch('requests.Session.get')
    def test_get_class_space_availability(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "classSpaces": [
                {
                    "courseId": "CHEM 1A",
                    "classSpaceAvailabilities": [
                        {"section": "0100", "enrollCode": "11111", "enrolledTotal": 100, "maxEnroll": 100}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_class_space_availability("20241")

        self.assertIn("Availability for Course: CHEM 1A", result)
        self.assertIn("Section: 0100 (Enroll Code: 11111)", result)
        self.assertIn("100 Enrolled out of 100 Max Capacity", result)

    @patch('requests.Session.get')
    def test_get_finals_has_finals(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hasFinals": True,
            "examDay": "Monday",
            "examDate": "June 10",
            "beginTime": "08:00 AM",
            "endTime": "11:00 AM",
            "comments": "Bring Scantron"
        }
        mock_get.return_value = mock_response

        result = self.client.get_finals({"enrollcode": "12345"})

        self.assertIn("Monday, June 10", result)
        self.assertIn("08:00 AM to 11:00 AM", result)
        self.assertIn("Bring Scantron", result)

    @patch('requests.Session.get')
    def test_get_finals_no_finals(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hasFinals": False
        }
        mock_get.return_value = mock_response

        result = self.client.get_finals({"enrollcode": "12345"})

        self.assertEqual(result, "No final exam is scheduled for this selection.")


if __name__ == '__main__':
    unittest.main()