import os,pandas as pd

from dit import Course as DC,Lecturer as DL,Classroom as DCL,Curricula as DCR
from udine import Lecturer,Course,Classroom,Curricula
from collections import namedtuple


class Importer:
    path_to_dit_courses=os.path.join('..','Datasets','dit_fall','dit_courses.xlsx')
    path_to_dit_classes=os.path.join('..','Datasets','dit_fall','dit_classrooms.xlsx')
    path_to_dit_lecturers=os.path.join('..','Datasets','dit_fall','teachers.csv')
    path_to_dit_curricula=os.path.join('..','Datasets','dit_fall')

    path_to_udine_datasets=os.path.join('..','Datasets','udine_datasets')

    udine_datasets=[
        'Udine1.ectt'
    ]

    @staticmethod
    def load_udine_dataset(pandas=False,udine_dataset_name=None):
        extra_info=dict()
        courses,rooms,lecturers,curricula,unavailability_constraints,room_constraints=list(),list(),list(),list(),list()
        Course_constraint=namedtuple('Course_constraint',field_names=['constraint_id','day','hperiod'])
        Room_constraint=namedtuple('Room_contsraint',field_names=['course_id','room_id'])
        with open(os.path.join(Importer.path_to_udine_datasets,udine_dataset_name),'r') as RF:
            for index,line in enumerate(RF):
                if line.strip()=="END.":
                    break

                if index<9:
                    desc,value=line.split(':')
                    extra_info[desc.strip()]=value.strip()
                    continue
                
                if line.strip()=="": 
                    continue
                
                if line.strip()=="COURSES:":
                    category="COURSES"
                    continue
                elif line.strip()=="ROOMS:":
                    category="ROOMS"
                    continue
                elif line.strip()=="CURRICULA":
                    category="CURRICULA"
                    continue
                elif line.strip()=="UNAVAILABILITY_CONSTRAINTS:":
                    category="UNAVAILABILITY_CONSTRAINTS"
                    continue
                elif line.strip()=="ROOM_CONSTRAINTS:":
                    category='ROOM_CONSTRAINTS'
                    continue
                
                data=line.split()
                if category=="COURSES":
                    if data[0].strip() not in courses:
                        courses.append(Course(data[0].strip(),data[1].strip(),int(data[2].strip()),int(data[3].strip()),int(data[4].strip())))
                    
                    if data[1].strip() not in lecturers:
                        lecturers.append(Lecturer(data[1].strip()))
                    
                    lecturers[lecturers.index(data[1].strip())].add_course(courses[courses.index(data[0].strip())])
                
                elif category=="ROOMS":
                    if data[0].strip() not in rooms:
                        rooms.append(Classroom(data[0].strip(),int(data[1].strip()),int(data[2].strip())))
                
                elif category=="CURRICULA":
                    if data[0].strip() not in curricula:
                        curricula.append(Curricula(data[0].strip()))
                    
                    for i in range(1,len(data)):
                        curricula[curricula.index(data[0].strip())].add_course(courses[courses.index(data[i])])
                
                elif category=="UNAVAILABILITY_CONSTRAINTS":
                    unavailability_constraints.append(Course_constraint._make(data))
                
                elif category=="ROOM_CONSTRAINT":
                    room_constraints.append(Room_constraint._make(data))
        
        # Work with dataframes
        if pandas:
            courses=pd.DataFrame(data=[list(course) for course in courses],columns=['ID','LECTURER',"#LECTURERS","#DISTINCT_PERIODS","STUDENTS"])
            lecturers=pd.DataFrame(data=[list(lecturer) for lecturer in lecturers],columns=['ID','COURSES'])
            classrooms=pd.DataFrame(data=[list(classr) for classr in classrooms],columns=['ID','CAPACITY','BUILDING_ID'])
            curricula=pd.DataFrame(data=[list(c) for c in curricula],columns=['ID','CURRICULA'])
            unavailability_constraints=pd.DataFrame(data=[list(x) for x in unavailability_constraints],columns=['COURSE_ID','DAY','HPERIOD'])
            room_constraints=pd.DataFrame(data=[list(x) for x in room_constraints],columns=['COURSE_ID','ROOM_ID'])
        return courses,lecturers,classrooms,curricula,unavailability_constraints,room_constraints


class Problem:
    def __init__(self,dataset_name,pandas=False):
        self.courses,self.lecturers,self.classrooms,self.curricula,self.unavailability_constraints,self.room_constraints=Importer.load_udine_dataset(dataset_name,pandas)
