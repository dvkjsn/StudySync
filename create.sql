-- Drop in dependency order
DROP TABLE IF EXISTS Availability;
DROP TABLE IF EXISTS GroupMembers;
DROP TABLE IF EXISTS Enrollments;
DROP TABLE IF EXISTS StudyGroups;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS Students;

-- Students taking part in StudySync
CREATE TABLE Students (
  email           VARCHAR(60) PRIMARY KEY,
  password        VARCHAR(128) NOT NULL,
  first_name      VARCHAR(30),
  last_name       VARCHAR(30),
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
  email      VARCHAR(60) NOT NULL,
  course_id  VARCHAR(10) NOT NULL,
  PRIMARY KEY (email, course_id),
  CONSTRAINT fk_enroll_student
    FOREIGN KEY (email) REFERENCES Students(email),
  CONSTRAINT fk_enroll_course
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);


-- Members of each study group
CREATE TABLE GroupMembers (
  group_id   VARCHAR(10) NOT NULL,
  email      VARCHAR(60) NOT NULL,
  role       VARCHAR(15),   -- leader / member
  PRIMARY KEY (group_id, email),
  CONSTRAINT fk_gm_group
    FOREIGN KEY (group_id) REFERENCES StudyGroups(group_id),
  CONSTRAINT fk_gm_student
    FOREIGN KEY (email) REFERENCES Students(email)
);


-- Time blocks that students are available to meet
CREATE TABLE Availability (
  availability_id VARCHAR(10) PRIMARY KEY,
  email           VARCHAR(60) NOT NULL,
  day_of_week     VARCHAR(10) NOT NULL,
  start_time      TIME        NOT NULL,
  end_time        TIME        NOT NULL,
  CONSTRAINT fk_avail_student
    FOREIGN KEY (email) REFERENCES Students(email)
);
