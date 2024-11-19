"""
Schedule class definition.
Represents a complete semester schedule with scoring methods.
"""

from dataclasses import dataclass
from typing import List, Dict, Set
import json
from pathlib import Path
from .course import Course, Stream
from datetime import datetime
from collections import defaultdict


@dataclass
class Schedule:
    """Represents a complete schedule with selected courses and streams"""
    semester: int  # 1 or 2
    year: int
    selected_streams: Dict[str, Stream]  # course_code -> selected_stream

    def add_stream(self, course_code: str, stream: Stream) -> None:
        """Add a stream to the schedule"""
        self.selected_streams[course_code] = stream

    def remove_course(self, course_code: str) -> None:
        """Remove a course from the schedule"""
        if course_code in self.selected_streams:
            del self.selected_streams[course_code]

    def has_conflicts(self) -> bool:
        """Check if there are any time conflicts in the schedule"""
        all_sessions = []
        # Collect all valid sessions with their course codes
        for code, stream in self.selected_streams.items():
            for session in stream.sessions:
                if session:
                    all_sessions.append((code, session))

        # Check each pair of sessions for conflicts between different courses
        for i, (code1, session1) in enumerate(all_sessions):
            for code2, session2 in all_sessions[i+1:]:
                if code1 != code2 and session1.conflicts_with(session2):
                    return True
        return False

    def get_conflicts(self) -> List[str]:
        """Get a list of all conflicts in the schedule"""
        conflicts = []
        all_sessions = []

        # Collect all valid sessions with their course codes
        for code, stream in self.selected_streams.items():
            for session in stream.sessions:
                if session:
                    all_sessions.append((code, session))

        # Check each pair of sessions for conflicts between different courses
        for i, (code1, session1) in enumerate(all_sessions):
            for code2, session2 in all_sessions[i+1:]:
                if code1 != code2 and session1.conflicts_with(session2):
                    conflicts.append(
                        f"Time conflict on {session1.day}: "
                        f"{code1} ({session1.start_time}-{session1.end_time}) "
                        f"vs {code2} ({session2.start_time}-{session2.end_time})"
                    )

        return conflicts

    def calculate_score(self, preferences: dict = None) -> float:
        """Calculate schedule score based on various criteria"""
        if preferences is None:
            preferences = {
                'early_class_threshold': 10,
                'late_class_threshold': 17,
                'preferred_days_off': ['FRI'],
                'weights': {
                    'days_off': 2.0,
                    'early_classes': 1.0,
                    'late_classes': 0.5,
                    'gaps': 0.5,
                    'long_days': 0.5,
                    'preferred_days': 3.0,
                    'level_distribution': 1.0
                }
            }

        score = 0.0
        weights = preferences['weights']

        all_sessions = []
        for stream in self.selected_streams.values():
            all_sessions.extend(session for session in stream.sessions if session)

        days_sessions = defaultdict(list)
        for session in all_sessions:
            days_sessions[session.day].append(session)
        for day in days_sessions:
            days_sessions[day].sort(key=lambda x: x.start_time)

        # Days off score
        days_with_classes = set(days_sessions.keys())
        score += (5 - len(days_with_classes)) * weights['days_off']

        # Early classes score
        early_classes = sum(
            1 for session in all_sessions
            if session.start_time.hour < preferences['early_class_threshold']
        )
        score -= early_classes * weights['early_classes']

        # Late classes score
        late_classes = sum(
            1 for session in all_sessions
            if session.end_time.hour >= preferences['late_class_threshold']
        )
        score -= late_classes * weights['late_classes']

        # Gaps between classes score
        for day_sessions in days_sessions.values():
            for i in range(len(day_sessions) - 1):
                gap = (day_sessions[i+1].start_time.hour -
                      day_sessions[i].end_time.hour)
                if gap == 1:
                    score += weights['gaps']
                elif gap > 3:
                    score -= (gap - 3) * weights['gaps']

        # Long days score
        for day_sessions in days_sessions.values():
            if not day_sessions:
                continue
            day_start = min(s.start_time.hour for s in day_sessions)
            day_end = max(s.end_time.hour for s in day_sessions)
            day_length = day_end - day_start
            if day_length > 6:
                score -= (day_length - 6) * weights['long_days']

        # Preferred days off score
        for day in preferences['preferred_days_off']:
            if day not in days_with_classes:
                score += weights['preferred_days']

        # Course level distribution score
        course_levels = [int(code[-3]) for code in self.selected_streams.keys()]
        if course_levels and (max(course_levels) - min(course_levels) <= 1):
            score += weights['level_distribution']

        return score

    def get_schedule_summary(self) -> dict:
        """Get a summary of schedule statistics"""
        all_sessions = []
        for stream in self.selected_streams.values():
            all_sessions.extend(session for session in stream.sessions if session)

        days_sessions = defaultdict(list)
        for session in all_sessions:
            days_sessions[session.day].append(session)

        early_classes = sum(1 for s in all_sessions if s.start_time.hour < 10)
        late_classes = sum(1 for s in all_sessions if s.end_time.hour >= 17)

        return {
            'total_courses': len(self.selected_streams),
            'days_with_classes': sorted(days_sessions.keys()),
            'early_classes': early_classes,
            'late_classes': late_classes,
            'course_levels': [int(code[-3]) for code in self.selected_streams.keys()],
            'score': self.calculate_score()
        }

    def print_schedule_stats(self):
        """Print readable schedule statistics"""
        stats = self.get_schedule_summary()
        print("\nSchedule Statistics:")
        print(f"Total Courses: {stats['total_courses']}")
        print(f"Days with Classes: {', '.join(stats['days_with_classes'])}")
        print(f"Early Classes (before 10 AM): {stats['early_classes']}")
        print(f"Late Classes (after 5 PM): {stats['late_classes']}")
        print(f"Course Levels: {sorted(stats['course_levels'])}")
        print(f"Overall Score: {stats['score']:.2f} (Higher is better)")

    def display_timetable(self):
        """Display a text-based weekly timetable"""
        DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        HOURS = list(range(8, 21))  # 8 AM to 8 PM

        # Get conflicts for highlighting
        conflicts = self.get_conflicts()
        conflict_times = defaultdict(list)
        for code1, session1, code2, session2 in conflicts:
            day = session1.day
            hour = session1.start_time.hour
            conflict_times[day].append(hour)

        # Create the header
        print("\nWeekly Schedule:")
        print("     ", end="")
        for day in DAYS:
            print(f"{day:^15}", end="")
        print("\n" + "-" * 80)

        # For each hour
        for hour in HOURS:
            # Print the hour marker
            print(f"{hour:02d}:00", end=" ")

            # For each day
            for day in DAYS:
                # Find any sessions that occur during this hour
                sessions = []
                for course_code, stream in self.selected_streams.items():
                    for session in stream.sessions:
                        if (session and session.day == day and
                                session.start_time.hour <= hour < session.end_time.hour):
                            sessions.append(course_code)

                # Print the cell content
                if sessions:
                    if hour in conflict_times[day]:
                        # Print conflicting sessions in red
                        print("\033[91m{}\033[0m".format(
                            ",".join(sessions).center(15)), end="")
                    else:
                        # Print multiple sessions separated by commas
                        print(f"{','.join(sessions):^15}", end="")
                else:
                    print(" " * 15, end="")
            print()  # New line for next hour

        print("-" * 80)

        # Print conflicts if any exist
        if conflicts:
            print("\nConflicts detected:")
            for code1, session1, code2, session2 in conflicts:
                print(f"  {code1} conflicts with {code2} on {session1.day} at "
                      f"{session1.start_time}-{session1.end_time}")

    def to_dict(self) -> dict:
        """Convert schedule to dictionary for JSON serialization"""
        return {
            'semester': self.semester,
            'year': self.year,
            'courses': {
                course_code: {
                    'class_code': stream.class_code,
                    'stream_name': stream.stream_name
                }
                for course_code, stream in self.selected_streams.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict, course_loader) -> 'Schedule':
        """Create schedule from dictionary representation"""
        selected_streams = {}
        for course_code, stream_info in data['courses'].items():
            course = course_loader.get_course_by_code(course_code)
            stream = next(
                s for s in course.streams
                if s.class_code == stream_info['class_code']
            )
            selected_streams[course_code] = stream

        return cls(
            semester=data['semester'],
            year=data['year'],
            selected_streams=selected_streams
        )

    def save_to_file(self, filepath: str) -> None:
        """Save schedule to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str, course_loader) -> 'Schedule':
        """Load schedule from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data, course_loader)
