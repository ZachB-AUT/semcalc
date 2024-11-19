from dataclasses import dataclass
from typing import List
from .session import Session

@dataclass
class Stream:
    """Represents a specific stream of a course"""
    class_code: str  # e.g., "ENGE501/W201"
    stream_name: str  # e.g., "A"
    sessions: List[Session]
    semester: int    # 1 or 2, derived from class code

    @classmethod
    def from_dict(cls, stream_dict: dict) -> 'Stream':
        """Create a Stream instance from a dictionary (JSON data)"""
        class_code = stream_dict['class']
        # Extract semester from class code (W1** = sem 1, W2** = sem 2)
        semester = 1 if 'W1' in class_code else 2

        return cls(
            class_code=class_code,
            stream_name=stream_dict['stream'],
            sessions=[Session.from_dict(s) for s in stream_dict['sessions']],
            semester=semester
        )

@dataclass
class Course:
    """Represents a course with all its available streams"""
    title: str
    course_code: str
    level: int
    points: float
    streams: List[Stream]

    @classmethod
    def from_dict(cls, course_dict: dict) -> 'Course':
        """Create a Course instance from a dictionary (JSON data)"""
        # Extract streams, filtering out any with invalid sessions
        streams = []
        for stream_data in course_dict['timetable']:
            try:
                stream = Stream.from_dict(stream_data)
                if stream.sessions:  # Only add streams that have valid sessions
                    streams.append(stream)
            except ValueError as e:
                print(f"Warning: Skipping invalid stream in {course_dict['course_code']}: {e}")
                continue

        return cls(
            title=course_dict['title'],
            course_code=course_dict['course_code'],
            level=int(course_dict['level']),
            points=float(course_dict['points']),
            streams=streams
        )

    def get_streams_for_semester(self, semester: int) -> List[Stream]:
        """Get all streams for a specific semester"""
        return [s for s in self.streams if s.semester == semester]

    def get_workload_indicator(self) -> float:
        """
        Returns a simple workload indicator based on course level
        Higher levels indicate potentially more difficult courses
        """
        return self.level / 100  # Simple scaling, can be made more sophisticated
