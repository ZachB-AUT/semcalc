"""
Core scheduling logic.
Generates possible course combinations that satisfy constraints.
"""

from typing import List
import copy
from semcalc.models.course import Course
from semcalc.models.schedule import Schedule
import itertools


class ScheduleGenerator:
    def __init__(self, courses: List[Course], semester: int, year: int,
                 sample_week: int = 3, verbose: bool = False):
        self.courses = courses
        self.semester = semester
        self.year = year
        self.valid_schedules: List[Schedule] = []
        self.verbose = verbose
        self.min_courses = 4
        self.max_courses = 4
        self.sample_week = sample_week

    def log(self, message: str):
        """Print message if verbose mode is on"""
        if self.verbose:
            print(message)

    def generate_schedules(self, max_schedules: int = 10) -> List[Schedule]:
        self.valid_schedules = []
        base_schedule = Schedule(
            semester=self.semester,
            year=self.year,
            selected_streams={}
        )

        self.log("\nStarting schedule generation...")
        self.log(f"Looking for schedules with {self.min_courses}-"
                 f"{self.max_courses} courses")
        self.log(f"Available courses: {[c.course_code for c in self.courses]}")
        self.log(f"Using sample week {self.sample_week}")

        for n in range(self.min_courses, self.max_courses + 1):
            self.log(f"\nTrying to create schedules with {n} courses")
            for course_subset in itertools.combinations(self.courses, n):
                sorted_courses = sorted(
                    course_subset,
                    key=lambda c: len([s for s in c.streams
                                      if s.semester == self.semester])
                )
                self._generate_recursive(
                    base_schedule,
                    list(sorted_courses),
                    max_schedules
                )

                if len(self.valid_schedules) >= max_schedules:
                    self.log("Found enough valid schedules, stopping search")
                    break

            if len(self.valid_schedules) >= max_schedules:
                break

        self.log(f"\nFound {len(self.valid_schedules)} valid schedules")

        # Sort schedules by score before returning
        sorted_schedules = sorted(
            self.valid_schedules,
            key=lambda s: s.calculate_score(),
            reverse=True  # Higher scores first
        )

        return sorted_schedules[:max_schedules]

    def _generate_recursive(
            self,
            current_schedule: Schedule,
            remaining_courses: List[Course],
            max_schedules: int
    ):
        """Recursively try different combinations of courses and streams"""
        if len(self.valid_schedules) >= max_schedules:
            return

        if not remaining_courses:
            self.log("\nFound valid schedule!")
            self.valid_schedules.append(copy.deepcopy(current_schedule))
            return

        current_course = remaining_courses[0]
        next_remaining = remaining_courses[1:]

        self.log(f"\nTrying to add {current_course.course_code}")
        self.log("Current partial schedule:")
        for code, strm in current_schedule.selected_streams.items():
            self.log(f"  {code}:")
            for session in strm.sessions:
                if session:
                    self.log(
                        f"    {session.day} {session.start_time}-"
                        f"{session.end_time}"
                    )

        valid_streams = [
            s for s in current_course.streams
            if s.semester == self.semester and any(ses for ses in s.sessions)
        ]

        for stream in valid_streams:
            self.log(f"\n  Trying stream {stream.class_code}:")
            for session in stream.sessions:
                if session:
                    self.log(
                        f"    {session.day} {session.start_time}-"
                        f"{session.end_time}"
                    )

            new_schedule = copy.deepcopy(current_schedule)
            new_schedule.add_stream(current_course.course_code, stream)

            conflicts = self._find_conflicts(new_schedule)
            if conflicts:
                self.log("    REJECTED due to conflicts:")
                for conflict in conflicts:
                    self.log(f"      {conflict}")
                continue

            self.log("    ACCEPTED - No conflicts, recursing...")
            self._generate_recursive(new_schedule, next_remaining, max_schedules)

    def _sort_courses_by_options(self) -> List[Course]:
        """Sort courses by number of valid streams for the semester"""
        def count_valid_streams(course: Course) -> int:
            return len([s for s in course.streams if s.semester == self.semester])

        valid_courses = [c for c in self.courses if count_valid_streams(c) > 0]
        return sorted(valid_courses, key=count_valid_streams)

    def _find_conflicts(self, schedule: Schedule) -> List[str]:
        """Find all conflicts in a schedule"""
        conflicts = []
        all_sessions = []
        for code, stream in schedule.selected_streams.items():
            for session in stream.sessions:
                if session:
                    all_sessions.append((code, session))

        for i, (code1, session1) in enumerate(all_sessions):
            for code2, session2 in all_sessions[i+1:]:
                if code1 != code2 and session1.conflicts_with(session2):
                    conflicts.append(
                        f"Conflict: {code1} ({session1.day} "
                        f"{session1.start_time}-{session1.end_time}) vs "
                        f"{code2} ({session2.day} "
                        f"{session2.start_time}-{session2.end_time})"
                    )
        return conflicts
