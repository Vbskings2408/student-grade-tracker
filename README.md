# Student Grade Tracker

A Python command-line app for recording course marks and credits, calculating SGPA and CGPA, and exporting a CSV report. It uses only the Python standard library.

## Quick start

Use Python 3.9 or later. From the project folder, run:

```bash
python3 tracker.py add 1 DBMS 85 4
python3 tracker.py add 1 MATH 72 3
python3 tracker.py add 2 JAVA 91 4
python3 tracker.py list
python3 tracker.py gpa
python3 tracker.py export grades.csv
```

The `add` arguments are semester, course code, marks out of 100, and credits. To correct a grade, run `add` again with the same semester and course code. To delete a record, run `python3 tracker.py remove 1 MATH`. Use `python3 tracker.py --help` for all commands. On Windows, you can use `py -3` in place of `python3`.

The example produces semester GPAs of 8.57 and 10.00 and a CGPA of 9.09. The CSV includes individual grades and all calculated GPAs. Export requires a new filename to protect existing files.

## How GPA is calculated

SGPA is the sum of credits multiplied by grade points, divided by the total credits for that semester. CGPA applies the same calculation to all saved courses across semesters, including failed courses. Rounding is applied only when displaying or exporting the result.

| Marks out of 100 | Grade points |
| --- | --- |
| 90 and above | 10 |
| 80 to below 90 | 9 |
| 70 to below 80 | 8 |
| 60 to below 70 | 7 |
| 50 to below 60 | 6 |
| 40 to below 50 | 5 |
| Below 40 | 0 |

This is a sample grading scale, independent of Chandigarh University's official rules. Edit `GRADE_SCALE` in `tracker.py` to use a different marks-to-points table.

## Local data

The default database is `~/.student-grade-tracker.json`. To keep different sets of records, put `--data PATH` before the command, for example `python3 tracker.py --data demo.json list`.
