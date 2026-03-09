import os
import requests
import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from langchain_core.documents import Document

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

    def _get_current_quarter_id(self) -> str:
        """
        Generates the UCSB quarter ID based on the current date.
        Format: YYYYQ where Q is 1 (Winter), 2 (Spring), 3 (Summer), 4 (Fall).
        """
        now = datetime.datetime.now()
        year = now.year
        month = now.month

        if 1 <= month <= 3:
            quarter = "1"  # Winter
        elif 4 <= month <= 6:
            quarter = "2"  # Spring
        elif 7 <= month <= 9:
            quarter = "3"  # Summer
        else:
            quarter = "4"  # Fall

        return f"{year}{quarter}"

    @staticmethod
    def _format_class_data(course: dict) -> str:
        """
        Helper function to flatten nested class JSON into a coherent RAG-friendly string.
        Safely handles null/None values from the API.
        """
        course_id = (course.get("courseId") or "").strip()
        title = (course.get("title") or "").strip()
        quarter = (course.get("quarter") or "").strip()
        desc = (course.get("description") or "").strip()
        college = (course.get("college") or "").strip()

        units = course.get("unitsFixed")
        if units is None or units == 0:
            units = f"{course.get('unitsVariableLow') or 0}-{course.get('unitsVariableHigh') or 0} (Variable)"

        rag_text = f"Course: {course_id} - {title} ({quarter})\n"
        rag_text += f"College: {college} | Units: {units}\n"
        rag_text += f"Description: {desc}\n"

        sections = course.get("classSections", [])
        if sections:
            rag_text += "Sections Availability and Details:\n"
            for sec in sections:
                enroll_code = (sec.get("enrollCode") or "").strip()
                section_id = (sec.get("section") or "").strip()
                enrolled = sec.get("enrolledTotal") or 0
                max_enroll = sec.get("maxEnroll") or 0
                instructors = [(inst.get("instructor") or "").strip() for inst in sec.get("instructors", []) if
                               inst.get("instructor")]
                instructor_str = ", ".join(instructors) if instructors else "TBD"

                time_locs = []
                for tl in sec.get("timeLocations", []):
                    days = (tl.get("days") or "").strip()
                    begin = (tl.get("beginTime") or "").strip()
                    end = (tl.get("endTime") or "").strip()
                    bldg = (tl.get("building") or "").strip()
                    room = (tl.get("room") or "").strip()

                    if days or begin:
                        time_locs.append(f"{days} {begin}-{end} at {bldg} {room}")

                time_str = " | ".join(time_locs) if time_locs else "TBA"

                rag_text += f"  - Section: {section_id} (Code: {enroll_code}) | Instructor(s): {instructor_str} | Schedule: {time_str} | Capacity: {enrolled}/{max_enroll} Enrolled\n"

        return rag_text.strip()

    def get_class_by_enrollcode(self, quarter: str, enrollcode: str) -> str:
        """1) GET /v3/classes/{quarter}/{enrollcode}"""
        url = f"{self.base_url}/v3/classes/{quarter}/{enrollcode}"
        response = self.session.get(url)

        if response.status_code == 200:
            return self._format_class_data(response.json())
        return f"Failed to fetch class. Status: {response.status_code}, Response: {response.text}"

    def get_all_classes_by_dept(self, dept_code: str = "") -> List[Document]:
        """2) GET /v3/classes/search -> Converted to Langchain Documents (Paginated)"""
        url = f"{self.base_url}/v3/classes/search"
        quarter = self._get_current_quarter_id()
        documents = []

        page_number = 1
        page_size = 100

        while True:
            params = {}
            if dept_code == "":
                params = {
                    "quarter": quarter,
                    "pageSize": page_size,
                    "pageNumber": page_number
                }
            else:
                params = {
                    "quarter": quarter,
                    "deptCode": dept_code,
                    "pageSize": page_size,
                    "pageNumber": page_number
                }

            response = self.session.get(url, params=params)

            if response.status_code != 200:
                print(
                    f"Failed to search classes on page {page_number}. Status: {response.status_code}, Response: {response.text}")
                break

            data = response.json()
            classes = data.get("classes", [])

            if not classes:
                break

            for course in classes:
                total_enrolled = 0
                total_max = 0
                for sec in course.get("classSections", []):
                    enrolled = sec.get("enrolledTotal")
                    max_cap = sec.get("maxEnroll")

                    total_enrolled += (enrolled if enrolled is not None else 0)
                    total_max += (max_cap if max_cap is not None else 0)

                remaining_availability = max(0, total_max - total_enrolled)

                course_id = course.get("courseId", "").strip()
                title = course.get("title", "").strip()
                course_name = f"{course_id} - {title}"

                page_content = self._format_class_data(course)
                doc = Document(
                    page_content=page_content,
                    metadata={
                        "course_name": course_name,
                        "remaining_total_availability": remaining_availability
                    }
                )
                documents.append(doc)

            if len(classes) < page_size:
                break

            page_number += 1

        return documents

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