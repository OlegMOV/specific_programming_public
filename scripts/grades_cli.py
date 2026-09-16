#!/usr/bin/env python3
"""CLI for adding/editing student ball and grade entries in assets/grades.json.

Data shape:
    {
      "students": ["01", "02", ...],
      "grades": {
        "01_LL": {"01": {"ball": 3.2, "grade": 4}, "02": null, ...},
        ...
      }
    }
"""
import argparse
import json
import sys
from pathlib import Path

DEFAULT_JSON_PATH = Path(__file__).resolve().parent.parent / "assets" / "grades.json"


def load(path):
    if not path.exists():
        return {"students": [], "grades": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_ball(value):
    if value is None or value == "":
        return None
    return float(value)


def parse_grade(value):
    if value is None or value == "":
        return None
    grade = int(value)
    if not 1 <= grade <= 5:
        raise ValueError("grade must be between 1 and 5")
    return grade


def cmd_set(args, data):
    if args.student not in data["students"]:
        raise SystemExit(f"Unknown student '{args.student}'. Add it first with add-student.")
    row = data["grades"].setdefault(args.lesson, {s: None for s in data["students"]})
    row[args.student] = {"ball": parse_ball(args.ball), "grade": parse_grade(args.grade)}
    print(f"Set {args.lesson} / {args.student} -> ball={row[args.student]['ball']} grade={row[args.student]['grade']}")


def cmd_clear(args, data):
    row = data["grades"].get(args.lesson)
    if row is None or args.student not in row:
        raise SystemExit(f"No entry for {args.lesson} / {args.student}")
    row[args.student] = None
    print(f"Cleared {args.lesson} / {args.student}")


def cmd_add_student(args, data):
    if args.student in data["students"]:
        raise SystemExit(f"Student '{args.student}' already exists")
    data["students"].append(args.student)
    for row in data["grades"].values():
        row.setdefault(args.student, None)
    print(f"Added student '{args.student}'")


def cmd_add_lesson(args, data):
    if args.lesson in data["grades"]:
        raise SystemExit(f"Lesson '{args.lesson}' already exists")
    data["grades"][args.lesson] = {s: None for s in data["students"]}
    print(f"Added lesson '{args.lesson}'")


def cmd_remove_lesson(args, data):
    if args.lesson not in data["grades"]:
        raise SystemExit(f"Lesson '{args.lesson}' not found")
    del data["grades"][args.lesson]
    print(f"Removed lesson '{args.lesson}'")


def cmd_remove_student(args, data):
    if args.student not in data["students"]:
        raise SystemExit(f"Student '{args.student}' not found")
    data["students"].remove(args.student)
    for row in data["grades"].values():
        row.pop(args.student, None)
    print(f"Removed student '{args.student}'")


def cmd_list(args, data):
    students = data["students"]
    lessons = [args.lesson] if args.lesson else list(data["grades"].keys())
    if args.lesson and args.lesson not in data["grades"]:
        raise SystemExit(f"Lesson '{args.lesson}' not found")

    col_width = max([len(s) for s in students] + [12]) + 2
    header = "lesson".ljust(10) + "".join(s.rjust(col_width) for s in students)
    print(header)
    for lesson in lessons:
        row = data["grades"].get(lesson, {})
        cells = []
        for s in students:
            entry = row.get(s)
            cells.append("--" if not entry else f"{entry['ball']}/{entry['grade']}")
        print(lesson.ljust(10) + "".join(c.rjust(col_width) for c in cells))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", type=Path, default=DEFAULT_JSON_PATH, help="path to grades.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="add or edit a student's ball/grade for a lesson")
    p_set.add_argument("lesson", help="lesson name, e.g. 25_GL")
    p_set.add_argument("student", help="student number, e.g. 01")
    p_set.add_argument("ball", help="ball value, e.g. 3.4 (or '' for none)")
    p_set.add_argument("grade", help="grade 1-5 (or '' for none)")
    p_set.set_defaults(func=cmd_set)

    p_clear = sub.add_parser("clear", help="clear a student's entry for a lesson (set to empty)")
    p_clear.add_argument("lesson")
    p_clear.add_argument("student")
    p_clear.set_defaults(func=cmd_clear)

    p_add_student = sub.add_parser("add-student", help="add a new student column")
    p_add_student.add_argument("student")
    p_add_student.set_defaults(func=cmd_add_student)

    p_remove_student = sub.add_parser("remove-student", help="remove a student column")
    p_remove_student.add_argument("student")
    p_remove_student.set_defaults(func=cmd_remove_student)

    p_add_lesson = sub.add_parser("add-lesson", help="add a new lesson row")
    p_add_lesson.add_argument("lesson")
    p_add_lesson.set_defaults(func=cmd_add_lesson)

    p_remove_lesson = sub.add_parser("remove-lesson", help="remove a lesson row")
    p_remove_lesson.add_argument("lesson")
    p_remove_lesson.set_defaults(func=cmd_remove_lesson)

    p_list = sub.add_parser("list", help="print the grades table")
    p_list.add_argument("--lesson", help="restrict to a single lesson")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    data = load(args.file)
    try:
        args.func(args, data)
    except ValueError as e:
        raise SystemExit(f"Error: {e}")
    if args.command != "list":
        save(args.file, data)


if __name__ == "__main__":
    main()
