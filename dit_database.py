import mysql
from enum import Enum
import socket,datetime,os
import bs4,requests
from mysql.connector import Error
from bs4 import BeautifulSoup as bs
from collections import defaultdict

class CCtype(Enum):
    AMFITHEATER=1,
    LABORATORY=2,
    TUTORING=3

    @staticmethod
    def name(id:int):
        return CCtype(id).name()
    
    @staticmethod
    def numeric(ctype:"CCtype"):
        return ctype.value

class Snifer:
    @staticmethod
    def establish_connection(configurations={}):
        conn=None
        try:
            conn=mysql.connector.connect(
                host=configurations['host'],
                user=configurations['user'],
                password=configurations['password'],
                port=configurations['port'],
                database=configurations['db'],
                auth_plugin='mysql_native_password'
            )
            print(f'Connection to {configurations["host"]} establish. Listening on port {configurations["port"]}')
        except Error as e:
            raise e
        return conn

    def __init__(self,configurations={}):
        self.configurations=configurations
        # self.conn=Snifer.establish_connection(configurations)
        # try:
        #     cursor=self.conn.cursor()
        #     cursor.execute("CREATE TABLE IF NOT EXISTS COURSE(id VARCHAR(20),name TEXT,semester INTEGER,theory INTEGER,laboratory INTEGER,tutoring INTEGER,credits INTEGER,PRIMARY KEY(id))")
        #     cursor.execute("CREATE TABLE IF NOT EXISTS LECTURER(id VARCHAR(20),name TEXT,id TEXT)")
        #     cursor.execute("CREATE TABLE IF NOT EXISTS ROOM(id VARCHAR(20),type TEXT,id TEXT)")
        #     cursor.execute("CREATE TABLE IF NOT EXISTS CURRICULA(id VARCHAR(20),CURRICULA_ID TEXT)")
        #     cursor.execute("CREATE TABLE IF NOT EXISTS ASSIGNMENT(course_id TEXT,lecturer_id TEXT,LECTURE_HOURS INTEGER,number_of_lectures INTEGER,type INTEGER,PRIMARY KEY(course_id,lecture_id),FOREIGN KEY(course_id,lecturer_name))")
        #     cursor.execute("CREATE TABLE IF NOT EXISTS SOLUTION(solution_pc TEXT,pc_cost INTEGER,course_id TEXT,lecture_id INTEGER,day INTEGER,period INTEGER,PRIMARY KEY(solution_id))")
        #     self.conn.commit()
        #     cursor.close()
        #     self.conn.close()
        # except Error as e:
        #     raise e.message()
    
    def insert(self,sql_query,values:tuple):
        self.conn=Snifer.establish_connection(self.configurations)
        try:
            cursor=self.conn.cursor()
            cursor.execute(sql_query,values)
            self.conn.commit()
            cursor.close()
            self.conn.close()
        except mysql.connector.Error as e:
            raise e.message()
    
    def fetch(self,table):
        self.conn=Snifer.establish_connection(self.configurations)
        try:
            cursor=self.conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            self.conn.commit()
            data=list(cursor.fetchall())
            cursor.close()
            self.conn.close()
            return data
        
        except Error as e:
            raise e.message()

    def insert_solution(self,course_id,lecture_id,day,period,cost):
        self.conn=Snifer.establish_connection(self.configurations)
        try:
            cursor=self.conn.cursor()
            cursor.execute(f'INSERT INTO SOLUTION(solution_pc,cost,course_id,lecture_id,day,period) VALUES(?,?,?,?,?)',(socket.gethostname(),cost,course_id,lecture_id,day,period))
            self.conn.commit()
            cursor.close()
            self.conn.close()
        except Error as e:
            raise e

    def get_classrooms(self):
        pass

    def get_lecturers(self):
        url="https://www.dit.uoi.gr/staff/"
        response=requests.get(url,verify=False)
        soup=bs(response.content,features='lxml')
        categories=[category.text.strip() for category in soup.find_all("h1")]
        dit_members=defaultdict(list)
        category_id=1

        for index,table in enumerate(soup.findAll("table")):
            start=True
            for tr in table.findAll("tr"):
                if start:
                    start=False
                    continue
                cells=tr.findAll("td")
                name=cells[0].text.strip()
                email_tel=cells[2].findAll("a")
                email=email_tel[0].text.strip()
                tel=email_tel[1].text.strip()
                dit_members[categories[index]].append((f'ditld{category_id}',name,email,tel))
                category_id+=1
        print(dit_members)


    def get_solution(self):
        self.conn=Snifer.establish_connection(self.configurations)
        try:
            cursor=self.conn.cursor()
            cursor.execute('SELECT * FROM SOLUTION WHERE solution_pc=?',(socket.gethostname(),))
            self.conn.commit()
            solutions={}
            for data in list(cursor.fetchall()):
                solutions[(data[1],data[2])]=(data[3],data[4])
            cursor.close()
            self.conn.close()
            return solutions

        except Error as e:
            raise e.message()


if __name__=='__main__':
    configurations={
        "host":"localhost",
        "user":"root",
        "password":"dbdit_2023",
        "port":8081,
        "db":"curriculum_dit"
    }

    snifer=Snifer(configurations)
    snifer.get_lecturers()




