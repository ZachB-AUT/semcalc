"""
Handles loading and processing of course JSON data.
Includes semester extraction and data validation.
"""

import json
from typing import List, Dict
from pathlib import Path
from semcalc.models.course import Course

class CourseLoader:
    def __init__(self, course_data_path: str, course_config_path: str):
        self.course_data_path = Path(course_data_path)
        self.course_config_path = Path(course_config_path)
        self.all_courses: Dict[str, dict] = {}
        self.required_courses: List[str] = []

    def load_all_courses(self) -> None:
        """Load the full course dataset and index it by course code"""
        with open(self.course_data_path, 'r') as f:
            courses = json.load(f)
            self.all_courses = {
                course['course_code']: course for course in courses
            }

    def validate_course_config(self) -> List[str]:
        """
        Validates that all courses in config exist in the course data.
        Returns a list of any missing courses.
        """
        if not self.all_courses:
            self.load_all_courses()
        if not self.required_courses:
            self.load_course_config()

        missing_courses = []
        for course_code in self.required_courses:
            if course_code not in self.all_courses:
                missing_courses.append(course_code)

        return missing_courses

    def load_course_config(self) -> None:
        """Load and validate the configuration specifying required courses"""
        with open(self.course_config_path, 'r') as f:
            config = json.load(f)
            self.required_courses = config['required_courses']

        missing = self.validate_course_config()
        if missing:
            raise ValueError(
                f"The following courses from config are not found in course data: {', '.join(missing)}"
            )

    def get_all_courses(self) -> List[Course]:
        """Get all available courses"""
        if not self.all_courses:
            self.load_all_courses()
        return [Course.from_dict(course_data)
                for course_data in self.all_courses.values()]

    def get_required_courses(self) -> List[Course]:
        """Get Course objects for all required courses"""
        if not self.all_courses:
            self.load_all_courses()
        if not self.required_courses:
            self.load_course_config()

        courses = []
        for course_code in self.required_courses:
            if course_code not in self.all_courses:
                raise KeyError(
                    f"Required course {course_code} not found in course data"
                )
            course_data = self.all_courses[course_code]
            courses.append(Course.from_dict(course_data))

        return courses

    def get_course_by_code(self, course_code: str) -> Course:
        """Get a specific course by its code"""
        if not self.all_courses:
            self.load_all_courses()
        if course_code not in self.all_courses:
            raise KeyError(f"Course {course_code} not found")
        return Course.from_dict(self.all_courses[course_code])
