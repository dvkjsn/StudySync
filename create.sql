-- Drop in dependency order
DROP TABLE IF EXISTS Availability;
DROP TABLE IF EXISTS GroupMembers;
DROP TABLE IF EXISTS Enrollments;
DROP TABLE IF EXISTS StudyGroups;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Students;

-- Students taking part in StudySync
CREATE TABLE Students (
  student_id      VARCHAR(10)  PRIMARY KEY,
  netid           VARCHAR(20)  NOT NULL UNIQUE,
  first_name      VARCHAR(30)  NOT NULL,
  last_name       VARCHAR(30)  NOT NULL,
  email           VARCHAR(60)  NOT NULL UNIQUE,
  major           VARCHAR(40),
  class_year      VARCHAR(15),
  preferred_mode  VARCHAR(10)   -- In-Person / Online / Hybrid
);

-- Courses
CREATE TABLE Courses (
  course_id      VARCHAR(10)  PRIMARY KEY,
  subject        VARCHAR(10)  NOT NULL,
  course_number  INT          NOT NULL,
  section        VARCHAR(5)   NOT NULL,
  title          VARCHAR(80)
);

-- Study groups created inside the system
CREATE TABLE StudyGroups (
  group_id      VARCHAR(10)  PRIMARY KEY,
  course_id     VARCHAR(10)  NOT NULL,
  group_name    VARCHAR(80)  NOT NULL,
  meeting_day   VARCHAR(10),
  start_time    TIME,
  end_time      TIME,
  meeting_mode  VARCHAR(10),   -- In-Person / Online / Hybrid
  max_size      INT,
  location      VARCHAR(80),
  CONSTRAINT fk_group_course
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

-- Which student is enrolled in which course
CREATE TABLE Enrollments (
  student_id  VARCHAR(10) NOT NULL,
  course_id   VARCHAR(10) NOT NULL,
  PRIMARY KEY (student_id, course_id),
  CONSTRAINT fk_enroll_student
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
  CONSTRAINT fk_enroll_course
    FOREIGN KEY (course_id)  REFERENCES Courses(course_id)
);

-- Members of each study group
CREATE TABLE GroupMembers (
  group_id    VARCHAR(10) NOT NULL,
  student_id  VARCHAR(10) NOT NULL,
  role        VARCHAR(15),   -- leader / member
  PRIMARY KEY (group_id, student_id),
  CONSTRAINT fk_gm_group
    FOREIGN KEY (group_id)   REFERENCES StudyGroups(group_id),
  CONSTRAINT fk_gm_student
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);

-- Time blocks that students are available to meet
CREATE TABLE Availability (
  availability_id VARCHAR(10) PRIMARY KEY,
  student_id      VARCHAR(10) NOT NULL,
  day_of_week     VARCHAR(10) NOT NULL,
  start_time      TIME        NOT NULL,
  end_time        TIME        NOT NULL,
  CONSTRAINT fk_avail_student
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);