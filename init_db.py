import sqlite3
from pathlib import Path
import csv

DB_PATH = Path(__file__).with_name("studysync.db")

schema_sql = """
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS Availability;
DROP TABLE IF EXISTS GroupMembers;
DROP TABLE IF EXISTS Enrollments;
DROP TABLE IF EXISTS StudyGroups;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Students;

PRAGMA foreign_keys = ON;

CREATE TABLE Students (
  email          TEXT PRIMARY KEY,
  password       TEXT NOT NULL,
  first_name     TEXT,
  last_name      TEXT,
  major          TEXT,
  class_year     TEXT,
  preferred_mode TEXT
);

CREATE TABLE Courses (
  course_id     TEXT PRIMARY KEY,
  subject       TEXT NOT NULL,
  course_number INTEGER NOT NULL,
  section       TEXT NOT NULL,
  title         TEXT
);

CREATE TABLE StudyGroups (
  group_id     TEXT PRIMARY KEY,
  course_id    TEXT NOT NULL,
  group_name   TEXT NOT NULL,
  meeting_day  TEXT,
  start_time   TEXT,
  end_time     TEXT,
  meeting_mode TEXT,
  max_size     INTEGER,
  location     TEXT,
  FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE Enrollments (
  email     TEXT NOT NULL,
  course_id TEXT NOT NULL,
  PRIMARY KEY (email, course_id),
  FOREIGN KEY (email) REFERENCES Students(email),
  FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE GroupMembers (
  group_id TEXT NOT NULL,
  email    TEXT NOT NULL,
  role     TEXT,
  PRIMARY KEY (group_id, email),
  FOREIGN KEY (group_id) REFERENCES StudyGroups(group_id),
  FOREIGN KEY (email) REFERENCES Students(email)
);

CREATE TABLE Availability (
  availability_id TEXT PRIMARY KEY,
  email           TEXT NOT NULL,
  day_of_week     TEXT NOT NULL,
  start_time      TEXT NOT NULL,
  end_time        TEXT NOT NULL,
  FOREIGN KEY (email) REFERENCES Students(email)
);
"""

def main():
    if DB_PATH.exists():
        DB_PATH.unlink()  # start clean each time for now

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Create schema
    cur.executescript(schema_sql)

    base = Path(__file__).parent

    # ---- Students ----
    with (base / "data" / "students.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["email"],
                r["password"],
                r["first_name"],
                r["last_name"],
                r["major"],
                r["class_year"],
                r["preferred_mode"],
            )
            for r in reader
        ]
    cur.executemany(
        """
        INSERT INTO Students
          (email, password, first_name, last_name, major, class_year, preferred_mode)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    # ---- Courses ----
    with (base / "data" /"courses.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["course_id"],
                r["subject"],
                int(r["course_number"]),
                r["section"],
                r["title"],
            )
            for r in reader
        ]
    cur.executemany(
        """
        INSERT INTO Courses
          (course_id, subject, course_number, section, title)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )

    # ---- StudyGroups ----
    with (base / "data" / "studygroups.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["group_id"],
                r["course_id"],
                r["group_name"],
                r["meeting_day"],
                r["start_time"],
                r["end_time"],
                r["meeting_mode"],
                int(r["max_size"]),
                r["location"],
            )
            for r in reader
        ]
    cur.executemany(
        """
        INSERT INTO StudyGroups
          (group_id, course_id, group_name, meeting_day, start_time, end_time,
           meeting_mode, max_size, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    # ---- Enrollments ----
    with (base / "data" /"enrollments.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [(r["email"], r["course_id"]) for r in reader]
    cur.executemany(
        "INSERT INTO Enrollments (email, course_id) VALUES (?, ?)",
        rows,
    )

    # ---- GroupMembers ----
    with (base / "data" /"groupmembers.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [(r["group_id"], r["email"], r["role"]) for r in reader]
    cur.executemany(
        "INSERT INTO GroupMembers (group_id, email, role) VALUES (?, ?, ?)",
        rows,
    )

    # ---- Availability ----
    with (base / "data" /"availability.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["availability_id"],
                r["email"],
                r["day_of_week"],
                r["start_time"],
                r["end_time"],
            )
            for r in reader
        ]
    cur.executemany(
        """
        INSERT INTO Availability
          (availability_id, email, day_of_week, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()
    conn.close()
    print("SQLite database created and CSV data loaded into studysync.db")

if __name__ == "__main__":
    main()
