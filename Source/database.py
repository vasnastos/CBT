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
        except:
            raise sqlite3.Error

    def create_tables(self):
        query = "CREATE TABLE IF NOT EXISTS COURSES(id VARCHAR(10),title TEXT,semester INTEGER,flow TEXT,theory_time INTEGER,lab_time INTEGER,tut_time INTEGER,credits INTEGER,PRIMARY KEY(title,semester))"
        query1 = "CREATE TABLE IF NOT EXISTS CLASSROOMS(id VARCHAR(10),type TEXT,capacity INTEGER,PRIMARY KEY(id))"
        query2 = "CREATE TABLE IF NOT EXISTS LECTURERS(name TEXT,rank TEXT,email TEXT,display_name TEXT,PRIMARY KEY(display_name))"
        query3 = "CREATE TABLE IF NOT EXISTS LECTURES(type INTEGER,duration INTEGER,classroom_id TEXT,lecturer_id TEXT,course_id TEXT,PRIMARY KEY(duration,type,classroom_id,lecturer_id,course_id))"
        query4 = "CREATE TABLE IF NOT EXISTS MEETINGS(classroom_id TEXT,lecturer_id TEXT,course_id TEXT,start_hour TEXT,end_hour TEXT,day TEXT,semester INTEGER,FOREIGN KEY(classroom_id) REFERENCES LECTURES(classroom_id),FOREIGN KEY(lecturer_id) REFERENCES LECTURES(lecturer_id),FOREIGN KEY(course_id) REFERENCES LECTURES(course_id),PRIMARY KEY(classroom_id,lecturer_id,course_id,day,start_hour,end_hour))"
        cur=self.conn.cursor()
        cur.execute(query)
        cur.execute(query1)
        cur.execute(query2)
        cur.execute(query3)
        cur.execute(query4)
        cur.close()
        self.conn.close()

    def insert_course(self, id, title, semester:int, flow, th:int, tl:int, tt:int, cr:int):
        self.conn=sqlite3.connect(self.database_name)
        query = "INSERT INTO COURSES(id,title,semester,flow,theory_time,lab_time,tut_time,credits) VALUES (?,?,?,?,?,?,?,?)"
        cur=self.conn.cursor()
        cur.execute(query, (id, title, semester, flow, th, tl, tt, cr))
        self.conn.commit()
        cur.close()
        self.conn.close()


    def insert_lecturer(self, name, rank:int, email, display_name):
        self.conn=sqlite3.connect(self.database_name)
        query = " INSERT INTO LECTURERS(name,rank,email,display_name) VALUES (?,?,?,?)"
        cur=self.conn.cursor()
        cur.execute(query, (name, rank, email, display_name))
        cur.close()
        self.conn.close()

    def insert_classsroom(self, id, type, capacity):
        self.conn=sqlite3.connect(self.database_name)
        query = "INSERT INTO CLASSROOMS(id,type,capacity) VALUES(?,?,?)"
        cur=self.conn.cursor()
        cur.execute(query, (id, type, capacity))
        self.conn.commit()
        self.conn.close()

    def insert_lecture(self, type, duration:int, cid, lid, crid):
        if self.lecture_exists(type,duration,cid,lid,crid): return
        self.conn=sqlite3.connect(self.database_name)
        query = "INSERT INTO LECTURES(type,duration,classroom_id,lecturer_id,course_id) VALUES(?,?,?,?,?)"
        cur=self.conn.cursor()
        cur.execute(query, (type, duration, cid, lid, crid))
        self.conn.commit()
        cur.close()
        self.conn.close()

    def insert_meeting(self, start_hour, end_hour, day, classroom_id,lecturer_id,course_id, semester:int):
        self.conn=sqlite3.connect(self.database_name)
        query = "INSERT INTO MEETINGS(classroom_id,lecturer_id,course_id,start_hour,end_hour,day,semester) VALUES(?,?,?,?,?,?,?)"
        cur=self.conn.cursor()
        cur.execute(query, (classroom_id,lecturer_id,course_id,start_hour, end_hour, day,semester))
        self.conn.commit()
        cur.close()
        self.conn.close()

    def lecture_exists(self,type,duration,classroom_id,lecturer_id,course_id):
        self.conn=sqlite3.connect(self.database_name)
        cur=self.conn.cursor()
        query="SELECT * FROM LECTURES WHERE type=? AND duration=? AND classroom_id=? AND lecturer_id=? AND course_id=?"
        cur.execute(query,(type,duration,classroom_id,lecturer_id,course_id))
        self.conn.commit()
        output=cur.fetchone()
        cur.close()
        self.conn.close()
        return output!=None


    # Get Data
    def courses(self):
        self.conn=sqlite3.connect(self.database_name)
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
        self.conn=sqlite3.connect(self.database_name)
        cur = self.conn.cursor()
        query = "SELECT * FROM CLASSROOMS"
        classrooms = list()
        output = cur.execute(query).fetchall()
        for row in output:
            classrooms.append(Classroom(row[0], row[1], row[2]))
        self.conn.commit()
        cur.close()
        self.conn.close()        
        return classrooms

    def lecturers(self):
        self.conn=sqlite3.connect(self.database_name)
        query = "SELECT * FROM LECTURERS"
        lecturers = list()
        cur = self.conn.cursor()
        output = cur.execute(query).fetchall()
        for row in output:
            lecturers.append(Lecturer(row[0], row[1], row[2], row[3]))
        self.conn.commit()
        cur.close()
        self.conn.close()
        return lecturers

    def lectures(self):
        self.conn=sqlite3.connect(self.database_name)
        query = "SELECT * FROM LECTURES"
        cur = self.conn.cursor()
        output = cur.execute(query).fetchall()
        lectures=list()
        for row in output:
            lectures.append(Lecture(row[0],row[1],row[2],row[3]))
        self.conn.commit()
        cur.close()
        self.conn.close()
        return lectures

    def meetings(self):
        self.conn=sqlite3.connect(self.database_name)
        query = "SELECT * FROM MEETINGS"
        query_course = "SELECT * FROM COURSE WHERE title=? and semester=?"
        query_lecture = "SELECT * FROM LECTURE WHERE meeting_id=?"
        meetings = list()
        cur = self.conn.cursor()
        output = cur.execute(query).fetchall()
        self.conn.commit()
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

        self.conn.close()
        return meetings
    
    def courses_to_txt(self):
        pathfile="dit_uoi_courses.txt"
        self.conn=sqlite3.connect(self.database_name)
        cur=self.conn.cursor()
        query="SELECT id,title,semester,credits FROM COURSES"
        output=cur.execute(query)
        with open(pathfile,'w') as WF:
            WF.write("ID,TITLE,SEMESTER,CREDITS\n")
            for id,title,semester,credits in output:
                WF.write(f"{id},{title},{semester},{credits}\n")
        print(f"File save as:{pathfile}")
