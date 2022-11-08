import os
import pandas as pd
from core import Room,Lecturer,Course,Assignment
from tabulate import tabulate
from itertools import product
from deprecated import deprecated
import networkx as nx

#Read data dit_winter_pregraduate.txt
class Problem:
    path_to_lecturers=os.path.join('','Datasets','dit_winter','dit_members.csv')
    path_to_courses=os.path.join('','Datasets','dit_winter','dit_courses.csv')
    path_to_rooms=os.path.join('','Datasets','dit_winter','dit_classrooms.csv')

    def __init__(self):
        self.id=None
        self.courses=dict()
        self.lectures=list()
        self.rooms=list()
        self.lecturers=dict()
        self.curriculas=dict()
        self.assignments=list()
        self.num_of_lectures=-1
        self.num_of_courses=-1
        self.num_of_rooms=-1
        self.num_of_lecturers=-1
        self.days=-1
        self.periods_per_day=-1
        self.G=nx.Graph()

    def reset(self):
        self.id=None
        self.courses.clear()
        self.lectures.clear()
        self.lecturers.clear()
        self.rooms.clear()
        self.curriculas.clear()
        self.num_of_lectures=-1
        self.num_of_courses=-1
        self.num_of_rooms=-1
        self.num_of_lecturers=-1
        self.days=-1
        self.periods_per_day=-1
        self.G.clear()
    
    def find_course(self,course_name):
        course_to_search=[course_id for course_id,course in self.courses.items() if course.name==course_name]
        if len(course_to_search)==0:
            return ""
        return course_to_search[0]

    @deprecated(version=0.1,reason="New function inserted after version 1.1")
    def read_instance(self,dataset_name):
        self.reset()
        self.id=dataset_name
        category=None
        with open(Problem.path_to_courses,'r',encoding='utf-8') as RF:
            cfg=dict()
            for line in RF:
                if line.startswith('#'): continue
                elif line.startswith('@'):
                    data=line.split(':')
                    cfg[data[0].strip().replace('@','')]=int(data[1].strip())
                if line=="COURSES":
                    category="COURSES"
                    continue
                elif line=="CURRICULA":
                    category="CURRICULA"
                    continue
                if category=="COURSES":
                    data=line.split(',')
                    self.courses[data[0].strip().upper()]=Course(data[0].strip(),data[1].strip().upper(),data[2].strip(),data[3].strip(),data[4].strip())
                elif category=="CURRICULA":
                    data=line.split(',')
                    self.curriculas[data[0].strip()]=[data[j].strip() for j in range(1,len(data))]

        self.days=cfg['days']
        self.periods_per_day=cfg['periods']
        self.senior_year_semesters=[]
        with open(Problem.path_to_lecturers,'r',encoding='utf-8') as RF:
            for line in RF:
                if line.startswith('#'): continue
                data=line.split(',')
                self.lecturers.append(Lecturer(data[0].strip(),data[1].strip().upper(),data[2].strip()))
            
        with open(Problem.path_to_rooms,'r',encoding='utf-8') as RF:
            for line in RF:
                if line.startswith('#'): continue
                data=line.split(',')
                self.rooms.append(Room(data[0].strip(),data[1].strip(),data[2].strip()))
        
        with open(dataset_name,'r',encoding='utf8') as RF:
            for line in RF:
                if line.startswith('#'): continue
                data=line.split(',')
                self.assignments.append(Assignment(data[0].strip().upper(),data[1].strip().upper(),int(data[2].strip()),int(data[3].strip())))

        
        for assignment in self.assignments:
            for lecture_id in range(self.courses[self.find_course(assignment.course_name)].theory_hours):
                self.lecturers[self.lectures.find(assignment.lecturer_name)].add_lecture((self.find_course(assignment.course_name),lecture_id))
            
        self.num_of_lectures=len(self.lectures)
        self.num_of_courses=len(self.courses)
        self.num_of_rooms=len(self.rooms)  
        self.num_of_lecturers=len(self.lecturers) 

        self.theories=[]
        self.laboratories=[]
        for _,course in self.courses:
            self.theories.extend(course.lectures)
            self.laboratories.extend(course.laboratories)

    def read_instance(self,dataset_filename):
        self.reset()
        cfg=dict()
        with open(os.path.join(Problem.path_to_courses,dataset_filename),'r') as RF:
            for i,line in enumerate(RF):
                if i<4:
                    data=line.split(':')
                    cfg[data[0].strip()]=data[1].strip()
                    continue

                if line.strip()=='COURSES':
                    category='COURSES'
                    continue
                elif line.strip()=="LECTURERS":
                    category='LECTURERS'
                    continue
                elif line.strip()=="CLASSROOMS":
                    category="CLASSROOMS"
                    continue
                elif line.strip()=="CURRICULA":
                    category="CURRICULA"
                    continue
                elif line.strip()=="ASSIGNMENT":
                    category="ASSIGNMENT"
                    continue
                elif line.strip()=="" or line.strip()=="#":
                    continue
                    
                data=line.split(',')
                if category=="COURSES":
                    self.courses.append(Course(data[0].strip(),data[1].strip(),int(data[2].strip()),int(data[3].strip()),int(data[4].strip()),int(data[5].strip()),int(data[6].strip())))                    
                elif category=="LECTURERS":
                    self.lecturers.append(Lecturer(data[0].strip(),data[1].strip(),data[2].strip()))
                elif category=="CLASSROOMS":
                    self.rooms.append(Room(data[0].strip(),data[1].strip(),int(data[2].strip())))
                elif category=="CURRICULA":
                    self.curriculas[data[0].strip()]=[data[i] for i in range(1,len(data))]
                elif category=="ASSIGNMENT":
                    self.assignments.append(Assignment(data[0].strip(),data[1].strip(),int(data[2].strip()),int(data[3].strip())))
        
        self.days=cfg['days']
        self.periods_per_day=cfg['periods_per_day']
        self.semesters=cfg['semesters']
        self.semester_courses={
            semester_id:[course.id for course in self.courses if course.semester==semester_id] 
            for semester_id in range(self.semesters)
        }
        self.num_of_lectures=len(self.lectures)
        self.num_of_courses=len(self.courses)
        self.num_of_rooms=len(self.rooms)  
        self.num_of_lecturers=len(self.lecturers)
        self.theories=[]
        self.laboratories=[]
        for _,course in self.courses:
            self.theories.extend(course.lectures)
            self.laboratories.extend(course.laboratories)

    def create_graph(self):
        self.G=nx.Graph()
        
        # 1. Courses in the same semester are conflicted to each other(1-6)
        course_identifiers=self.courses.keys()
        for course_index1 in range(len(course_identifiers)):
            for course_index2 in range(course_index1+1,len(course_identifiers)):
                if self.courses[course_identifiers[course_index1]].semester==self.courses[course_identifiers[course_index2]].semester:
                    self.G.add_node(course_identifiers[course_index1],course_identifiers[course_index2])

        # 2. Curriculas are assembled by the courses of the 7 and 8 semester.
        for _,curricula_courses in self.curriculas:
            for index1 in range(len(curricula_courses)):
                for index2 in range(index1+1,len(curricula_courses)):
                    self.G.add_edge(curricula_courses[index1],curricula_courses[index2])

        # 3. Courses that are taken by the same lecturer are conflicted to each other.
        for lecturer in self.lecturers:
            lecturer_courses=list({course_id for (course_id,_) in lecturer.lectures})
            for course_index1 in range(len(lecturer_courses)):
                for course_index2 in range(course_index1+1,len(lecturer_courses)):
                    if  not self.G.has_edge(lecturer_courses[course_index1],lecturer_courses[course_index2]):
                        self.G.add_edge(lecturer_courses[course_index1],lecturer_courses[course_index2])


    def get_semester_laboratory_courses(self,semester_id):
        return [
            course_id 
            for course_id,course in self.courses.items()
            if course.semester==semester_id and course.laboratory_hours>0
        ]

    def laboratory_combinations(self,semester_id):
        courses_with_labs=self.get_semester_laboratory_courses(semester_id)
        return list(product(*[self.courses[course_id].laboratory for course_id in courses_with_labs if self.courses[course_id].semester==semester_id],len(courses_with_labs)))

    def __str__(self):
        output=f'Dataset:{self.id}\n'
        output+=f'Courses:{self.num_of_courses}\n'
        output+=f'Lecturers:{self.num_of_lecturers}\n'
        output+=f'Rooms:{self.num_of_rooms}\n'
        output+=f'Lectures:{self.num_of_lectures}\n'
        output+=str(tabulate([course.to_list() for _,course in self.courses.items()]),headers=['COURSE_ID','COURSE_NAME'],table_fmt='fancy_grid')+'\n'
        output+=str(tabulate([lecturer.to_list() for _,lecturer in self.lecturers.items()],headers=['ID','EMAIL','USER_NAME'],tablefmt='fancy_grid'))+'\n'
        output+=str(tabulate([room.to_list() for _,room in self.rooms.items()]),headers=['ID','ROOM TYPE','CAPACITY'])+'\n'
        return output
    