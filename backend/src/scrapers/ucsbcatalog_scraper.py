import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class UCSBCatalogClient:
    def __init__(self):
        self.base_url = "https://api.ucsb.edu/academics/curriculums"
        self.session = requests.Session()
        api_key = os.getenv("UCSB_API_KEY")
        if not api_key:
            raise ValueError("UCSB_API_KEY not found. Please ensure it is set in your .env file.")
        self.session.headers.update({
            "ucsb-api-key": api_key,
            "Accept": "application/json"
        })

    @staticmethod
    def _format_class_data(course: dict) -> str:
        """
        Helper function to flatten nested class JSON into a coherent RAG-friendly string.
        """
        course_id = course.get("courseId", "").strip()
        title = course.get("title", "").strip()
        quarter = course.get("quarter", "")
        desc = course.get("description", "").strip()
        college = course.get("college", "")

        units = course.get("unitsFixed")
        if units is None or units == 0:
            units = f"{course.get('unitsVariableLow', 0)}-{course.get('unitsVariableHigh', 0)} (Variable)"

        rag_text = f"Course: {course_id} - {title} ({quarter})\n"
        rag_text += f"College: {college} | Units: {units}\n"
        rag_text += f"Description: {desc}\n"

        sections = course.get("classSections", [])
        if sections:
            rag_text += "Sections Availability and Details:\n"
            for sec in sections:
                enroll_code = sec.get("enrollCode", "")
                section_id = sec.get("section", "")
                enrolled = sec.get("enrolledTotal", 0)
                max_enroll = sec.get("maxEnroll", 0)

                instructors = [inst.get("instructor", "").strip() for inst in sec.get("instructors", []) if
                               inst.get("instructor")]
                instructor_str = ", ".join(instructors) if instructors else "TBD"

                time_locs = []
                for tl in sec.get("timeLocations", []):
                    days = tl.get("days", "").strip()
                    begin = tl.get("beginTime", "").strip()
                    end = tl.get("endTime", "").strip()
                    bldg = tl.get("building", "").strip()
                    room = tl.get("room", "").strip()
                    if days or begin:
                        time_locs.append(f"{days} {begin}-{end} at {bldg} {room}")
                time_str = " | ".join(time_locs) if time_locs else "TBA"

                rag_text += f"  - Section: {section_id} (Code: {enroll_code}) | Instructor(s): {instructor_str} | Schedule: {time_str} | Capacity: {enrolled}/{max_enroll} Enrolled\n"

        return rag_text.strip()

    def get_class_by_enrollcode(self, quarter: str, enrollcode: str) -> str:
        """1) GET /v3/classes/{quarter}/{enrollcode}"""
        url = f"{self.base_url}/v3/classes/{quarter}/{enrollcode}"
        # Notice we use self.session.get() instead of requests.get()
        response = self.session.get(url)

        if response.status_code == 200:
            return self._format_class_data(response.json())
        return f"Failed to fetch class. Status: {response.status_code}, Response: {response.text}"

    def search_classes(self, params: Dict[str, Any]) -> str:
        """2) GET /v3/classes/search"""
        url = f"{self.base_url}/v3/classes/search"
        response = self.session.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            classes = data.get("classes", [])
            if not classes:
                return "No classes found matching the search criteria."

            formatted_classes = [self._format_class_data(c) for c in classes]
            return "\n\n---\n\n".join(formatted_classes)
        return f"Failed to search classes. Status: {response.status_code}, Response: {response.text}"

    def get_class_section(self, quarter: str, enrollcode: str) -> str:
        """3) GET /v3/classsection/{quarter}/{enrollcode}"""
        url = f"{self.base_url}/v3/classsection/{quarter}/{enrollcode}"
        response = self.session.get(url)

        if response.status_code == 200:
            return self._format_class_data(response.json())
        return f"Failed to fetch class section. Status: {response.status_code}, Response: {response.text}"

    def get_class_space_availability(self, quarter: str, params: Optional[Dict[str, Any]] = None) -> str:
        """4) GET /v3/classspaceavailability/{quarter}"""
        url = f"{self.base_url}/v3/classspaceavailability/{quarter}"
        response = self.session.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            spaces = data.get("classSpaces", [])
            if not spaces:
                return "No class space availability data found."

            output = []
            for space in spaces:
                course_id = space.get("courseId", "").strip()
                for avail in space.get("classSpaceAvailabilities", []):
                    sec = avail.get("section", "").strip()
                    code = avail.get("enrollCode", "").strip()
                    enrolled = avail.get("enrolledTotal", 0)
                    maximum = avail.get("maxEnroll", 0)
                    output.append(
                        f"Availability for Course: {course_id} | Section: {sec} (Enroll Code: {code}) -> {enrolled} Enrolled out of {maximum} Max Capacity.")

            return "\n".join(output)
        return f"Failed to fetch space availability. Status: {response.status_code}, Response: {response.text}"

    def get_finals(self, params: Dict[str, Any]) -> str:
        """5) GET /v3/finals"""
        url = f"{self.base_url}/v3/finals"
        response = self.session.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            has_finals = data.get("hasFinals", False)

            if not has_finals:
                return "No final exam is scheduled for this selection."

            day = data.get("examDay", "").strip()
            date = data.get("examDate", "").strip()
            begin = data.get("beginTime", "").strip()
            end = data.get("endTime", "").strip()
            comments = data.get("comments", "").strip()

            rag_text = f"Final Exam Details:\n- Date: {day}, {date}\n- Time: {begin} to {end}"
            if comments:
                rag_text += f"\n- Comments: {comments}"

            return rag_text
        return f"Failed to fetch finals data. Status: {response.status_code}, Response: {response.text}"