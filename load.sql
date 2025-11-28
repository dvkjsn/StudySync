-- Load data into updated schema (email is the primary key)


-- Students
LOAD DATA LOCAL INFILE 'students.csv'
INTO TABLE Students
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(email, password, first_name, last_name, major, class_year, preferred_mode);


-- Courses
LOAD DATA LOCAL INFILE 'courses.csv'
INTO TABLE Courses
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(course_id, subject, course_number, section, title);


-- Study Groups
LOAD DATA LOCAL INFILE 'studygroups.csv'
INTO TABLE StudyGroups
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(group_id, course_id, group_name, meeting_day, start_time, end_time,
 meeting_mode, max_size, location);


-- Enrollments  (email → course)
LOAD DATA LOCAL INFILE 'enrollments.csv'
INTO TABLE Enrollments
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(email, course_id);


-- Group Members (email → group)
LOAD DATA LOCAL INFILE 'groupmembers.csv'
INTO TABLE GroupMembers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(group_id, email, role);


-- Availability (email → availability slots)
LOAD DATA LOCAL INFILE 'availability.csv'
INTO TABLE Availability
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(availability_id, email, day_of_week, start_time, end_time);
