import pytest
from pathlib import Path
from semcalc.data_handler.json_loader import CourseLoader
from semcalc.models.course import Course

# Test data paths
SAMPLE_DATA_PATH = "semcalc/input/all_courses.json"
CONFIG_PATH = "semcalc/input/course_config.json"

def test_course_loader_initialization():
    loader = CourseLoader(SAMPLE_DATA_PATH, CONFIG_PATH)
    assert loader.course_data_path.exists(), "Course data file should exist"
    assert loader.course_config_path.exists(), "Course config file should exist"

def test_load_all_courses():
    loader = CourseLoader(SAMPLE_DATA_PATH, CONFIG_PATH)
    loader.load_all_courses()
    assert len(loader.all_courses) > 0, "Should load at least one course"
    assert "ENGE501" in loader.all_courses, "Sample course should be present"

def test_load_course_config():
    loader = CourseLoader(SAMPLE_DATA_PATH, CONFIG_PATH)
    loader.load_course_config()
    assert len(loader.required_courses) > 0, "Should have at least one required course"

def test_get_required_courses():
    loader = CourseLoader(SAMPLE_DATA_PATH, CONFIG_PATH)
    courses = loader.get_required_courses()
    assert all(isinstance(course, Course) for course in courses)
    assert len(courses) == len(loader.required_courses)

def test_invalid_course_code():
    loader = CourseLoader(SAMPLE_DATA_PATH, CONFIG_PATH)
    # Modify required_courses to include an invalid code
    loader.load_course_config()
    loader.required_courses.append("INVALID101")

    with pytest.raises(KeyError):
        loader.get_required_courses()

def test_course_data_integrity():
    loader = CourseLoader(SAMPLE_DATA_PATH, CONFIG_PATH)
    courses = loader.get_required_courses()

    for course in courses:
        assert course.title, "Course should have a title"
        assert course.course_code, "Course should have a code"
        assert course.level > 0, "Course should have a valid level"
        assert course.points > 0, "Course should have valid points"
        assert len(course.streams) > 0, "Course should have at least one stream"
