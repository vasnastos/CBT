import sqlite3
from Source.classroom import Classroom
from Source.course import Course
from Source.lecturer import Lecturer
from Source.lecture import Lecture
from Source.meeting import Meeting
from Source.time_ import convert2timegap


class database:
    def __init__(self, name):
        self.database_name = name
        try:
            self.conn = sqlite3.connect(self.database_name)
            self.cur = self.conn.cursor()
        except:
            raise sqlite3.Error

    def create_tables(self):
        query = "CREATE TABLE IF NOT EXISTS COURSES(id VARCHAR(10),title TEXT,semester INTEGER,flow TEXT,theory_time INTEGER,lab_time INTEGER,tut_time INTEGER,credits INTEGER,PRIMARY KEY(title,semester))"
        query1 = "CREATE TABLE IF NOT EXISTS CLASSROOMS(id VARCHAR(10),type TEXT,capacity INTEGER,PRIMARY KEY(id))"
        query2 = "CREATE TABLE IF NOT EXISTS LECTURERS(name TEXT,rank TEXT,email TEXT,display_name TEXT,PRIMARY KEY(display_name))"
        query3 = "CREATE TABLE IF NOT EXISTS MEETINGS(mid TEXT,start_hour TEXT,end_hour TEXT,day TEXT,ltoken TEXT,semester INTEGER,PRIMARY KEY(mid))"
        query4 = "CREATE TABLE IF NOT EXISTS LECTURES(type INTEGER,duration INTEGER,classroom_id TEXT,lecturer_id TEXT,meeting_id TEXT)"
        self.cur.execute(query)
        self.cur.execute(query1)
        self.cur.execute(query2)
        self.cur.execute(query3)
        self.cur.execute(query4)

    def insert_course(self, id, title, semester, flow, th, tl, tt, cr):
        query = "INSERT INTO COURSES(id,title,semester,flow,theory_time,lab_time,tut_time,credits) VALUES (?,?,?,?,?,?,?)"
        self.conn.execute(query, (id, title, semester, flow, th, tl, tt, cr))

    def insert_lecturer(self, name, rank, email, display_name):
        query = " INSERT INTO LECTURERS(name,rank,email,display_name) VALUES (?,?,?,?)"
        self.cur.execute(query, (name, rank, email, display_name))

    def insert_classsroom(self, id, type, capacity):
        query = "INSERT INTO CLASSROOMS(id,type,capacity) VALUES(?,?,?)"
        self.cur.execute(query, (id, type, capacity))

    def insert_lecture(self, type, duration, cid, lid, mid):
        query = "INSERT INTO LECTURES(type,duration,classroom_id,lecturer_id,meeting_id) VALUES(?,?,?,?)"
        self.cur.execute(query, (type, duration, cid, lid, mid))

    def insert_meeting(self, start_hour, end_hour, day, lesson, semester):
        query = "INSERT INTO MEETINGS(mid,start_hour,end_hour,day,ltoken,semester) VALUES(?,?,?,?,?,?,?)"
        self.cur.execute(query, (start_hour, end_hour, day, lesson, semester))

    def courses(self):
        cur = self.conn.cursor()
        lessons = list()
        query = "SELECT * FROM COURSES"
        output = cur.execute(query).fetchall()
        for row in output:
            lessons.append(
                Course(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        cur.close()
        return lessons

    def classrooms(self):
        cur = self.conn.cursor()
        query = "SELECT * FROM CLASSROOMS"
        classrooms = list()
        output = cur.execute(query).fetchall()
        for row in output:
            classrooms.append(Classroom(row[0], row[1], row[2]))
        cur.close()
        return classrooms

    def lecturers(self):
        query = "SELECT * FROM LECTURERS"
        lecturers = list()
        cur = self.conn.cursor()
        output = cur.execute(query).fetchall()
        for row in output:
            lecturers.append(Lecturer(row[0], row[1], row[2], row[3]))
        cur.close()
        return lecturers

    def lectures(self):
        query = "SELECT * FROM LECTURES"
        cur = self.conn.cursor()
        output = cur.execute(query).fetchall()
        for row in output:
            pass
        self.cur.close()

    def meetings(self):
        query = "SELECT * FROM MEETINGS"
        query_course = "SELECT * FROM COURSE WHERE title=? and semester=?"
        query_lecture = "SELECT * FROM LECTURE WHERE meeting_id=?"
        meetings = list()
        cur = self.conn.cursor()
        output = cur.execute(query).fetchall()
        for row in output:
            cname = row[4].split("_")
            title = cname[0]
            semester = cname[1]
            cursor_course = self.conn.cursor()
            get_query_course = cursor_course.execute(
                query, (title, semester)).fetchone()
            query_course = Course(
                get_query_course[0], get_query_course[1], get_query_course[2], get_query_course[3], get_query_course[4], get_query_course[5], get_query_course[6], get_query_course[7])
            self.meetings.append(
                Meeting(row[0], row[1], row[2], row[3], query_course, row[5])
            )
            cursor_course.close()
            lecture_cursor = self.conn.cursor()
            lecture_record = lecture_cursor.execute(
                query_lecture, (row[0])).fetchone()
            lecture_instance = Lecture(
                lecture_record[0], lecture_record[1], lecture_record[2], lecture_record[3]
            )
            lecture_cursor.close()

            meetings.append(
                Meeting(row[0], row[1], row[2], row[3],
                        query_course, row[5], lecture_instance)
            )
        cur.close()
        return meetings
