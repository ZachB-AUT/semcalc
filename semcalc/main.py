"""
Main entry point for the semester calculator.
Handles CLI interface and program flow.
"""

from semcalc.data_handler.json_loader import CourseLoader
from typing import List
from semcalc.models.course import Course
from semcalc.models.schedule import Schedule
from pathlib import Path
from semcalc.scheduler.schedule_generator import ScheduleGenerator


def display_courses(courses: List[Course], detail_level: int = 1):
    """
    Display courses with different levels of detail
    detail_level:
        1 = basic info (code, title, level)
        2 = includes streams
        3 = includes full timetable
    """
    for course in courses:
        print(f"\nCourse: {course.course_code} - {course.title}")
        print(f"Level: {course.level}")
        print(f"Points: {course.points}")

        if detail_level >= 2:
            print("Available Streams:")
            for stream in course.streams:
                print(f"  Stream: {stream.class_code}")
                if detail_level >= 3:
                    print("  Sessions:")
                    for session in stream.sessions:
                        if session:
                            print(f"    {session.day} {session.start_time}-"
                                  f"{session.end_time}, Room: {session.room}")
        print("-" * 50)


def manage_schedule(loader: CourseLoader):
    """Handle schedule creation and modification"""
    schedule = Schedule(semester=1, year=2024, selected_streams={})

    while True:
        print("\nSchedule Management")
        print("1. Add Course to Schedule")
        print("2. Remove Course from Schedule")
        print("3. View Current Schedule")
        print("4. Display Timetable")
        print("5. Save Schedule")
        print("6. Load Schedule")
        print("7. Check for Conflicts")
        print("8. View Schedule Statistics")
        print("9. Generate Schedule")
        print("10. Return to Main Menu")

        choice = input("\nEnter your choice (1-10): ")

        if choice == "1":
            course_code = input("Enter course code: ").upper()
            try:
                course = loader.get_course_by_code(course_code)
                print("\nAvailable streams:")
                for i, stream in enumerate(course.streams, 1):
                    print(f"{i}. {stream.class_code}")
                stream_choice = int(input("Select stream number: ")) - 1
                schedule.add_stream(course_code, course.streams[stream_choice])
            except (KeyError, IndexError, ValueError) as e:
                print(f"Error: {e}")

        elif choice == "2":
            course_code = input("Enter course code to remove: ").upper()
            schedule.remove_course(course_code)

        elif choice == "3":
            print("\nCurrent Schedule:")
            for course_code, stream in schedule.selected_streams.items():
                print(f"\n{course_code} - {stream.class_code}")
                for session in stream.sessions:
                    if session:
                        print(f"  {session.day} {session.start_time}-"
                              f"{session.end_time}, Room: {session.room}")

        elif choice == "4":
            schedule.display_timetable()

        elif choice == "5":
            filepath = input("Enter filename to save (will be saved in "
                          "schedules/): ")
            filepath = f"semcalc/schedules/{filepath}.json"
            Path("semcalc/schedules").mkdir(exist_ok=True)
            schedule.save_to_file(filepath)
            print("Schedule saved!")

        elif choice == "6":
            filepath = input("Enter filename to load: ")
            filepath = f"semcalc/schedules/{filepath}.json"
            try:
                schedule = Schedule.load_from_file(filepath, loader)
                print("Schedule loaded!")
            except FileNotFoundError:
                print("File not found!")

        elif choice == "7":
            if schedule.has_conflicts():
                print("Warning: Schedule has time conflicts!")
            else:
                print("No conflicts found in schedule.")

        elif choice == "8":
            schedule.print_schedule_stats()

        elif choice == "9":
            required_courses = loader.get_required_courses()
            semester = int(input("Enter semester (1 or 2): "))
            sample_week = int(input("Enter sample week (default 3): ") or "3")
            verbose = input("Enable verbose output? (y/n): ").lower() == 'y'
            generator = ScheduleGenerator(
                courses=required_courses,
                semester=semester,
                year=schedule.year,
                sample_week=sample_week,
                verbose=verbose
            )
            print(f"\nGenerating schedules using Week {sample_week} as sample...")
            schedules = generator.generate_schedules(max_schedules=5)

            if schedules:
                print(f"\nFound {len(schedules)} possible schedules:")
                for i, s in enumerate(schedules, 1):
                    print(f"\nSchedule {i}:")
                    s.print_schedule_stats()
                    s.display_timetable()
                    print("-" * 80)

                choice = input("\nSelect a schedule to use (1-5, or 'n'): ")
                if choice.isdigit() and 1 <= int(choice) <= len(schedules):
                    schedule = schedules[int(choice)-1]
                    print("Schedule selected!")
            else:
                print("No valid schedules found.")

        elif choice == "10":
            break


def main():
    # Initialize the course loader
    loader = CourseLoader(
        course_data_path="semcalc/input/all_courses.json",
        course_config_path="semcalc/input/course_config.json"
    )

    while True:
        print("\nSemester Calculator - Main Menu")
        print("1. Display All Available Courses")
        print("2. Display Required Courses")
        print("3. Display Course Details")
        print("4. Manage Schedule")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ")

        if choice == "1":
            print("\nAll Available Courses:")
            all_courses = loader.get_all_courses()
            display_courses(all_courses, detail_level=1)

        elif choice == "2":
            print("\nRequired Courses:")
            required_courses = loader.get_required_courses()
            display_courses(required_courses, detail_level=1)

        elif choice == "3":
            course_code = input("Enter course code (e.g., ENGE501): ").upper()
            try:
                course = loader.get_course_by_code(course_code)
                display_courses([course], detail_level=3)
            except KeyError:
                print(f"Course {course_code} not found.")

        elif choice == "4":
            manage_schedule(loader)

        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
