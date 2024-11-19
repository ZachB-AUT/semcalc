import pytest
from semcalc.scheduler.schedule_generator import ScheduleGenerator
from semcalc.models.course import Course, Stream
from semcalc.models.session import Session
from datetime import datetime, time

def create_test_session(day: str, start_hour: int, end_hour: int) -> Session:
    """Helper function to create test sessions"""
    return Session(
        starting_date=datetime.strptime("01-Mar-2024", "%d-%b-%Y"),
        ending_date=datetime.strptime("30-Jun-2024", "%d-%b-%Y"),
        day=day,
        start_time=time(start_hour),
        end_time=time(end_hour),
        room="TEST"
    )

def create_test_course(code: str, stream_times: list) -> Course:
    """Helper function to create test courses with specified stream times"""
    streams = []
    for i, times in enumerate(stream_times):
        sessions = []
        for day, start, end in times:
            sessions.append(create_test_session(day, start, end))

        streams.append(Stream(
            class_code=f"{code}/W101",
            stream_name=f"Stream{i}",
            sessions=sessions,
            semester=1
        ))

    return Course(
        title=f"Test Course {code}",
        course_code=code,
        level=5,
        points=15.0,
        streams=streams
    )

def test_basic_schedule_generation():
    """Test basic schedule generation with non-conflicting courses"""
    # Create two courses with non-conflicting streams
    course1 = create_test_course("TEST101", [
        [("MON", 9, 11)],  # Stream 1
        [("TUE", 9, 11)]   # Stream 2
    ])

    course2 = create_test_course("TEST102", [
        [("WED", 9, 11)],  # Stream 1
        [("THU", 9, 11)]   # Stream 2
    ])

    generator = ScheduleGenerator([course1, course2], semester=1, year=2024)
    schedules = generator.generate_possible_schedules()

    assert len(schedules) > 0, "Should generate at least one valid schedule"
    assert len(schedules[0].selected_streams) == 2, "Should include both courses"

def test_conflicting_schedules():
    """Test schedule generation with some conflicting options"""
    # Create courses with overlapping times
    course1 = create_test_course("TEST201", [
        [("MON", 9, 11)],  # Stream 1
        [("TUE", 9, 11)]   # Stream 2
    ])

    course2 = create_test_course("TEST202", [
        [("MON", 10, 12)],  # Stream 1 (conflicts with course1 Stream 1)
        [("WED", 9, 11)]    # Stream 2 (no conflicts)
    ])

    generator = ScheduleGenerator([course1, course2], semester=1, year=2024)
    schedules = generator.generate_possible_schedules()

    # Should still find valid combinations (course1 Stream 2 + either stream of course2)
    assert len(schedules) > 0, "Should find valid non-conflicting combinations"

    # Check that none of the generated schedules have conflicts
    for schedule in schedules:
        assert not schedule.has_conflicts(), "Generated schedule should not have conflicts"

def test_no_valid_schedules():
    """Test case where no valid schedules are possible"""
    # Create courses where all streams conflict
    course1 = create_test_course("TEST301", [
        [("MON", 9, 11)],  # Only stream
    ])

    course2 = create_test_course("TEST302", [
        [("MON", 10, 12)],  # Only stream, conflicts with course1
    ])

    generator = ScheduleGenerator([course1, course2], semester=1, year=2024)
    schedules = generator.generate_possible_schedules()

    assert len(schedules) == 0, "Should not generate any schedules when all combinations conflict"

def test_schedule_scoring():
    """Test schedule scoring functionality"""
    # Create courses with different time patterns
    early_course = create_test_course("TEST401", [
        [("MON", 8, 10)],  # Early morning class
    ])

    good_time_course = create_test_course("TEST402", [
        [("TUE", 11, 13)],  # Mid-day class
    ])

    generator = ScheduleGenerator([early_course, good_time_course], semester=1, year=2024)
    schedules = generator.generate_possible_schedules()

    # Score schedules
    scores = [generator.score_schedule(schedule) for schedule in schedules]
    assert len(scores) > 0, "Should generate and score at least one schedule"

def test_max_schedules_limit():
    """Test that the generator respects the maximum schedule limit"""
    # Create courses with many possible combinations
    course1 = create_test_course("TEST501", [
        [("MON", 9, 11)],
        [("TUE", 9, 11)],
        [("WED", 9, 11)]
    ])

    course2 = create_test_course("TEST502", [
        [("THU", 9, 11)],
        [("FRI", 9, 11)]
    ])

    max_schedules = 3
    generator = ScheduleGenerator([course1, course2], semester=1, year=2024)
    schedules = generator.generate_possible_schedules(max_schedules=max_schedules)

    assert len(schedules) <= max_schedules, "Should not exceed maximum schedule limit"
