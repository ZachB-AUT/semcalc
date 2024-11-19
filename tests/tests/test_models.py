import pytest
from datetime import datetime, time
from semcalc.models.session import Session
from semcalc.models.course import Stream, Course

# Sample JSON data for testing
SAMPLE_SESSION_DICT = {
    "starting": "23-Jul-2025",
    "ending": "22-Oct-2025",
    "day": "WED",
    "time": "4:00 PM - 6:00 PM",
    "room": "WA220"
}

SAMPLE_STREAM_DICT = {
    "class": "ENGE600/W201",
    "stream": "A",
    "sessions": [SAMPLE_SESSION_DICT]
}

SAMPLE_COURSE_DICT = {
    "title": "Engineering Management",
    "course_code": "ENGE600",
    "level": "6",
    "points": "15.00",
    "timetable": [SAMPLE_STREAM_DICT]
}

class TestSession:
    def test_session_from_dict(self):
        session = Session.from_dict(SAMPLE_SESSION_DICT)
        assert session.day == "WED"
        assert session.room == "WA220"
        assert session.start_time == time(16, 0)  # 4:00 PM
        assert session.end_time == time(18, 0)    # 6:00 PM

    def test_session_conflict_detection(self):
        session1 = Session.from_dict({
            "starting": "23-Jul-2025",
            "ending": "22-Oct-2025",
            "day": "WED",
            "time": "2:00 PM - 4:00 PM",
            "room": "WA220"
        })

        # Same day, overlapping time
        session2 = Session.from_dict({
            "starting": "23-Jul-2025",
            "ending": "22-Oct-2025",
            "day": "WED",
            "time": "3:00 PM - 5:00 PM",
            "room": "WB220"
        })

        # Same day, non-overlapping time
        session3 = Session.from_dict({
            "starting": "23-Jul-2025",
            "ending": "22-Oct-2025",
            "day": "WED",
            "time": "4:00 PM - 6:00 PM",
            "room": "WA220"
        })

        # Different day
        session4 = Session.from_dict({
            "starting": "23-Jul-2025",
            "ending": "22-Oct-2025",
            "day": "THU",
            "time": "2:00 PM - 4:00 PM",
            "room": "WA220"
        })

        assert session1.conflicts_with(session2)  # Should conflict
        assert not session1.conflicts_with(session3)  # Should not conflict
        assert not session1.conflicts_with(session4)  # Different days

class TestStream:
    def test_stream_from_dict(self):
        stream = Stream.from_dict(SAMPLE_STREAM_DICT)
        assert stream.class_code == "ENGE600/W201"
        assert stream.stream_name == "A"
        assert stream.semester == 2  # W2** indicates semester 2
        assert len(stream.sessions) == 1

class TestCourse:
    def test_course_from_dict(self):
        course = Course.from_dict(SAMPLE_COURSE_DICT)
        assert course.title == "Engineering Management"
        assert course.course_code == "ENGE600"
        assert course.level == 6
        assert course.points == 15.0
        assert len(course.streams) == 1

    def test_get_streams_for_semester(self):
        course = Course.from_dict(SAMPLE_COURSE_DICT)
        sem2_streams = course.get_streams_for_semester(2)
        sem1_streams = course.get_streams_for_semester(1)
        assert len(sem2_streams) == 1  # Our sample stream is semester 2
        assert len(sem1_streams) == 0  # No semester 1 streams in sample

    def test_workload_indicator(self):
        course = Course.from_dict(SAMPLE_COURSE_DICT)
        assert course.get_workload_indicator() == 0.06  # level 6 -> 6/100
