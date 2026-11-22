"""Store marks, calculate credit-weighted GPAs, and export a CSV report."""

import argparse
import csv
import json
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

GRADE_SCALE = [(90, 10), (80, 9), (70, 8), (60, 7), (50, 6), (40, 5), (0, 0)]
DEFAULT_DATA = Path.home() / ".student-grade-tracker.json"


def grade_points(marks):
    return next(points for minimum, points in GRADE_SCALE if marks >= minimum)


def weighted_gpa(records):
    return sum(row["credits"] * grade_points(row["marks"]) for row in records) / sum(
        row["credits"] for row in records
    )


def validate_record(semester, course, marks, credits):
    if semester < 1 or not course.strip():
        raise ValueError("Enter a positive semester number and a course code.")
    if not 0 <= marks <= 100:
        raise ValueError("Marks must be between 0 and 100.")
    if not math.isfinite(credits) or not 0 < credits <= 100:
        raise ValueError("Credits must be greater than 0 and at most 100.")
    return dict(semester=semester, course=course.strip().upper(), marks=marks, credits=credits)


def load_records(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    try:
        if not isinstance(data, list):
            raise ValueError("Expected a list of records.")
        records = []
        keys = set()
        for row in data:
            if (
                type(row["semester"]) is not int
                or type(row["marks"]) not in (int, float)
                or type(row["credits"]) not in (int, float)
            ):
                raise ValueError("Invalid field types.")
            record = validate_record(row["semester"], row["course"], row["marks"], row["credits"])
            key = record["semester"], record["course"]
            if key in keys:
                raise ValueError("Duplicate semester and course.")
            keys.add(key)
            records.append(record)
        return records
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid grade data in {path}: {error}") from error


def save_records(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as temp:
        temporary_path = Path(temp.name)
        try:
            with temp:
                json.dump(records, temp, indent=2)
                temp.write("\n")
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)


def semester_gpas(records):
    groups = {}
    for row in records:
        groups.setdefault(row["semester"], []).append(row)
    return [(semester, weighted_gpa(rows)) for semester, rows in sorted(groups.items())]


def export_report(path, records):
    with path.open("x", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Semester", "Course", "Marks / 100", "Credits", "Grade points"])
        for row in records:
            course = row["course"]
            if course.startswith(("=", "+", "-", "@")):
                course = "'" + course
            writer.writerow([row["semester"], course, row["marks"], row["credits"], grade_points(row["marks"])])
        writer.writerow([])
        writer.writerow(["Semester", "Metric", "GPA / 10"])
        for semester, gpa in semester_gpas(records):
            writer.writerow([semester, "SGPA", f"{gpa:.2f}"])
        writer.writerow(["All", "CGPA", f"{weighted_gpa(records):.2f}"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to the JSON grade file")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in [
        ("add", "Add a course or update an existing course in the same semester"),
        ("remove", "Remove a course from a semester"),
    ]:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("semester", type=int)
        command.add_argument("course")
        if name == "add":
            command.add_argument("marks", type=float)
            command.add_argument("credits", type=float)
    commands.add_parser("list", help="List saved courses")
    commands.add_parser("gpa", help="Show semester and cumulative GPAs")
    commands.add_parser("export", help="Export course grades and GPAs to a new CSV file").add_argument(
        "output", type=Path
    )
    args = parser.parse_args()

    try:
        records = load_records(args.data)
        if args.command in ("add", "remove"):
            course = args.course.strip().upper()
            others = [row for row in records if (row["semester"], row["course"]) != (args.semester, course)]
            if args.command == "add":
                others.append(validate_record(args.semester, course, args.marks, args.credits))
            elif len(others) == len(records):
                raise ValueError("Course not found in that semester.")
            save_records(args.data, others)
            print(f"{'Saved' if args.command == 'add' else 'Removed'} {course} (semester {args.semester}).")
            return 0

        if not records:
            print("No courses saved. Use the add command to get started.")
            return 1 if args.command == "export" else 0

        records.sort(key=lambda row: (row["semester"], row["course"]))
        if args.command == "list":
            for row in records:
                print(f"Semester {row['semester']} | {row['course']} | {row['marks']:g}/100 | "
                      f"{row['credits']:g} credits | {grade_points(row['marks'])} points")
        elif args.command == "gpa":
            for semester, gpa in semester_gpas(records):
                print(f"Semester {semester} SGPA: {gpa:.2f}")
            print(f"CGPA: {weighted_gpa(records):.2f}")
        else:
            export_report(args.output, records)
            print(f"Report written to {args.output}")
        return 0
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
