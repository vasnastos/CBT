import sqlite3 

class database:
    def __init__(self):
        self.conn=sqlite3.connect("lessons.db")
        self.conn.execute("CREATE TABLE lessons_dnm (id int(6) NOT NULL,title varchar(80) NOT NULL,semester varchar(100) DEFAULT NULL);")
        self.conn.execute("CREATE TABLE IF NOT EXISTS teachers()")
        print("Database Created")

    def insert_course(self,id,name,semester):
        pass
