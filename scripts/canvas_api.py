#!/usr/bin/env python3
"""
Canvas API utility script for managing course data.

This script provides basic Canvas API functions for retrieving course information,
student lists, and other course-related data.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from canvasapi import Canvas


# Configure logging with basicConfig
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    # Define log message format
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)


# Constants
CANVAS_URL: str = "https://georgetown.instructure.com"
TOKEN_FILE: str = ".canvastoken"


def _get_canvas_token(token_file_path: Optional[str] = None) -> str:
    """
    Read Canvas API token from file.

    Args:
        token_file_path: Path to the token file. If None, looks in repo root.

    Returns:
        Canvas API token as string.

    Raises:
        FileNotFoundError: If token file doesn't exist.
        ValueError: If token file is empty.
    """
    if token_file_path is None:
        repo_root = Path(__file__).parent.parent
        token_file_path = repo_root / TOKEN_FILE

    token_path = Path(token_file_path)

    if not token_path.exists():
        raise FileNotFoundError(
            f"Canvas token file not found at {token_path}. "
            f"Please create {TOKEN_FILE} with your Canvas API token."
        )

    token = token_path.read_text().strip()

    if not token:
        raise ValueError(f"Canvas token file at {token_path} is empty.")

    logger.debug(f"Successfully read Canvas token from {token_path}")
    return token


def _initialize_canvas(canvas_url: str = CANVAS_URL) -> Canvas:
    """
    Initialize Canvas API client.

    Args:
        canvas_url: Canvas instance URL.

    Returns:
        Initialized Canvas API client.
    """
    token = _get_canvas_token()
    canvas = Canvas(canvas_url, token)
    logger.info(f"Initialized Canvas API client for {canvas_url}")
    return canvas


def get_user_info() -> dict:
    """
    Get information about the authenticated user.

    Returns:
        Dictionary containing user information.
    """
    canvas = _initialize_canvas()
    user = canvas.get_current_user()

    user_info = {
        "id": user.id,
        "name": user.name,
        "email": getattr(user, "email", None),
        "login_id": getattr(user, "login_id", None),
    }

    logger.info(f"Retrieved user info for: {user_info['name']}")
    return user_info


def list_courses() -> list[dict]:
    """
    List all courses for the authenticated user.

    Returns:
        List of dictionaries containing course information.
    """
    canvas = _initialize_canvas()
    courses = canvas.get_courses()

    course_list = []
    for course in courses:
        course_info = {
            "id": getattr(course, "id", None),
            "name": getattr(course, "name", None),
            "course_code": getattr(course, "course_code", None),
            "workflow_state": getattr(course, "workflow_state", None),
        }
        course_list.append(course_info)

    logger.info(f"Retrieved {len(course_list)} courses")
    return course_list


def find_course_by_name(course_name: str) -> Optional[dict]:
    """
    Find a course by name or course code.

    Args:
        course_name: Name or course code to search for (case-insensitive).

    Returns:
        Dictionary with course info if found, None otherwise.
    """
    courses = list_courses()
    course_name_lower = course_name.lower()

    for course in courses:
        name = course.get("name", "").lower()
        code = course.get("course_code", "").lower()

        if course_name_lower in name or course_name_lower in code:
            logger.info(f"Found course: {course['name']} (ID: {course['id']})")
            return course

    logger.warning(f"Course not found: {course_name}")
    return None


def get_course_students(course_id: int) -> list[dict]:
    """
    Get list of students enrolled in a course.

    Args:
        course_id: Canvas course ID.

    Returns:
        List of dictionaries containing student information.
    """
    canvas = _initialize_canvas()
    course = canvas.get_course(course_id)

    students = course.get_users(enrollment_type=["student"])

    student_list = []
    for student in students:
        student_info = {
            "id": student.id,
            "name": student.name,
            "sortable_name": getattr(student, "sortable_name", None),
            "email": getattr(student, "email", None),
            "login_id": getattr(student, "login_id", None),
        }
        student_list.append(student_info)

    logger.info(f"Retrieved {len(student_list)} students from course {course_id}")
    return student_list


def get_course_assignments(course_id: int) -> list[dict]:
    """
    Get list of assignments for a course.

    Args:
        course_id: Canvas course ID.

    Returns:
        List of dictionaries containing assignment information.
    """
    canvas = _initialize_canvas()
    course = canvas.get_course(course_id)

    assignments = course.get_assignments()

    assignment_list = []
    for assignment in assignments:
        assignment_info = {
            "id": assignment.id,
            "name": assignment.name,
            "due_at": getattr(assignment, "due_at", None),
            "points_possible": getattr(assignment, "points_possible", None),
            "submission_types": getattr(assignment, "submission_types", None),
        }
        assignment_list.append(assignment_info)

    logger.info(f"Retrieved {len(assignment_list)} assignments from course {course_id}")
    return assignment_list


def main():
    """Main function to demonstrate Canvas API usage."""
    import json

    logger.info("Starting Canvas API demo")

    # Get user info
    logger.info("\n=== User Information ===")
    user_info = get_user_info()
    print(json.dumps(user_info, indent=2, default=str))

    # List all courses
    logger.info("\n=== All Courses ===")
    courses = list_courses()
    print(json.dumps(courses[:5], indent=2, default=str))  # Show first 5

    # Find DSAN 6725 course
    logger.info("\n=== Finding DSAN 6725 Course ===")
    dsan_course = find_course_by_name("6725")
    if dsan_course:
        print(json.dumps(dsan_course, indent=2, default=str))

        # Get students from the course
        logger.info("\n=== Course Students ===")
        students = get_course_students(dsan_course["id"])
        print(json.dumps(students, indent=2, default=str))

        # Get assignments
        logger.info("\n=== Course Assignments ===")
        assignments = get_course_assignments(dsan_course["id"])
        print(json.dumps(assignments[:5], indent=2, default=str))  # Show first 5
    else:
        logger.error("DSAN 6725 course not found")


if __name__ == "__main__":
    main()
