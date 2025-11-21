-- Load data from CSV files created for Task C.

LOAD DATA LOCAL INFILE 'students.csv'
INTO TABLE Students
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(student_id, netid, first_name, last_name, email, major, class_year, preferred_mode);

LOAD DATA LOCAL INFILE 'courses.csv'
INTO TABLE Courses
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(course_id, subject, course_number, section, title);

LOAD DATA LOCAL INFILE 'studygroups.csv'
INTO TABLE StudyGroups
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(group_id, course_id, group_name, meeting_day, start_time, end_time,
 meeting_mode, max_size, location);

LOAD DATA LOCAL INFILE 'enrollments.csv'
INTO TABLE Enrollments
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(student_id, course_id);

LOAD DATA LOCAL INFILE 'groupmembers.csv'
INTO TABLE GroupMembers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(group_id, student_id, role);

LOAD DATA LOCAL INFILE 'availability.csv'
INTO TABLE Availability
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(availability_id, student_id, day_of_week, start_time, end_time);