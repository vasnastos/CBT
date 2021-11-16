import sqlite3
from Source.classroom import Classroom
from Source.course import Course
from Source.lecturer import Lecturer
from Source.lecture import Lecture
from Source.meeting import Meeting
from Source.time_ import convert2timegap
import os


class Cbt_database:
    def __init__(self, name):
        self.database_name = name
        try:
            self.conn = sqlite3.connect(self.database_name)
        except:
            raise sqlite3.Error

    def create_tables(self):
        query = "CREATE TABLE IF NOT EXISTS COURSES(id VARCHAR(10),title TEXT,semester INTEGER,flow TEXT,theory_time INTEGER,lab_time INTEGER,tut_time INTEGER,credits INTEGER,PRIMARY KEY(id))"
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
            lecturers.append(Lecturer(row[3],row[0],row[2],row[1]))
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
        classroom_query="SELECT * FROM CLASSROOMS WHERE id=?"
        lecturer_query="SELECT * FROM LECTURERS WHERE display_name=?"
        course_query="SELECT * FROM COURSES WHERE id=?"
        for row in output:
            classroom_cursor=self.conn.cursor()
            lecturer_cursor=self.conn.cursor()
            course_cursor=self.conn.cursor()
            classroom_record=classroom_cursor.execute(classroom_query,(row[2],)).fetchall()[0]
            lecturer_record=lecturer_cursor.execute(lecturer_query,(row[3],)).fetchall()[0]
            course_record=course_cursor.execute(course_query,(row[4],)).fetchall()[0]
            classroom_cursor.close()
            lecturer_cursor.close()
            course_cursor.close()
            lectures.append(Lecture(row[0],row[1],Classroom(classroom_record[0],classroom_record[1],classroom_record[2]),Lecturer(lecturer_record[3],lecturer_record[0],lecturer_record[2],lecturer_record[1]),Course(course_record[0],course_record[1],course_record[2],course_record[3],course_record[4],course_record[5],course_record[6],course_record[7])))
        self.conn.commit()
        cur.close()
        self.conn.close()
        return lectures

    def meetings(self):
        self.conn=sqlite3.connect(self.database_name)
        query = "SELECT * FROM MEETINGS"
        meetings = list()
        cur = self.conn.cursor()
        output = cur.execute(query).fetchall()
        for row in output:
            course_cursor=self.conn.cursor()
            lecturer_cursor = self.conn.cursor()
            classroom_cursor=self.conn.cursor()
            classroom_query="SELECT * FROM CLASSROOMS WHERE id=?"
            lecturer_query="SELECT * FROM LECTURERS WHERE display_name=?"
            course_query="SELECT * FROM COURSES WHERE id=?"
            course_record=course_cursor.execute(course_query,(row[2],)).fetchall()[0]
            self.conn.commit()
            course_cursor.close()
            lecturer_record = lecturer_cursor.execute(lecturer_query, (row[1],)).fetchall()[0]
            self.conn.commit()
            lecturer_cursor.close()
            classroom_record=classroom_cursor.execute(classroom_query,(row[0],)).fetchall()[0]
            self.conn.commit()
            classroom_cursor.close()
            meetings.append(Meeting(row[3], row[4], row[5], row[6],Course(course_record[0],course_record[1],course_record[2],course_record[3],course_record[4],course_record[5],course_record[6],course_record[7]),Lecturer(lecturer_record[3],lecturer_record[0],lecturer_record[2],lecturer_record[1]), Classroom(classroom_record[0],classroom_record[1],classroom_record[2])))
            course_cursor.close()
            lecturer_cursor.close()
            classroom_cursor.close()
        cur.close()

        self.conn.close()
        return meetings
    
    def export_meetings(self):
        query="SELECT * FROM MEETINGS"
        cursor=self.conn.cursor()
        out=cursor.execute(query).fetchall()
        self.conn.commit()
        outputpath=os.path.join('','dbexport')
        if not os.path.exists(outputpath):
            os.mkdir(outputpath)
        with open(os.path.join(outputpath,'meetings.csv')) as WF:    
            WF.write('Classroom,lecturer,course,start_hour,end_hour,day,semester\n')
            for rec in out:
                WF.write(f"{rec[0]},{rec[1]},{rec[2]},{rec[3]},{rec[4]},{rec[5]},{rec[6]}\n")
        self.conn.close()


