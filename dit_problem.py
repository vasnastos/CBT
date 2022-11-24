import os
import networkx as nx
from core import Course, Room, Lecturer
from collections import defaultdict

class Course:
    def __init__(self,cid,cname,csemester,ctheory_hours,ctutoring_hours,clab_hours,ccredits,clab_hours_in_use):
        self.id=cid
        self.name=cname
        self.semester=csemester
        self.theory_hours=ctheory_hours
        self.tutoring_hours=ctutoring_hours
        self.lab_hours=clab_hours
        self.credits=ccredits
        self.lab_hours_in_use=clab_hours_in_use
    
    def assign_lecture(self):
        self.lab_hours_in_use+=1

    def assert_valid(self):
        assert(self.lab_hours_in_use==self.lab_hours)    

    def begin_theory(self):
        return 0
    
    def end_theory(self):
        return self.theory_hours

    def begin_tutoring(self):
        return self.theory_hours
    
    def end_tutoring(self):
        return self.theory_hours+self.tutoring_hours

    def begin_lab(self):
        return self.theory_hours+self.tutoring_hours

    def end_lab(self):
        return self.theory_hours+self.tutoring_hours+self.lab_hours
    
    def __eq__(self,obj):
        return self.id==obj.id


class Problem:  
    path_to_datasets=os.path.join('','Datasets','dit_datasets','dit_winter_pregraduate.txt')
    def __init__(self):
        self.confs=dict()
        self.courses=dict()
        self.rooms=list()
        self.lecturers=defaultdict(list)
        self.curriculas=defaultdict(list)
        self.events=list()
        with open(Problem.path_to_datasets,'r',encoding='utf8') as RF:
            for i,line in enumerate(RF):
                if i<6:
                    data=line.split(':')
                    self.confs[data[0].replace(':','').strip()]=data[1]
            
                if len(line)==0 or line.startswith("#"):
                    continue
                
                if line=="COURSES":
                    category="COURSES"
                    continue
                elif line=="LECTURERS":
                    category="LECTURERS"
                    continue
                elif line=="CLASSROOMS":
                    category="ROOMS"
                    continue
                elif line=="CURRICULA":
                    category="CURRICULA"
                    continue
                elif line=="ASSIGNMENTS":
                    category="ASSIGNMENTS"
                    continue
                
                data=line.split(',')
                if category=="COURSES":
                    self.courses[data[0]]=Course(data[0],data[1],int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6]),0))
                elif category=="LECTURERS":
                    self.lecturers[data[0]]={"email":data[1],"username":data[2],"courses":list()}
                elif category=="ROOMS":
                    self.rooms.append(tuple(data))
                elif category=="ASSIGNMENTS":
                    self.assignments[data[1].upper()].append((data[0],int(data[2]),int(data[3]),data[4]))
                elif category=="CURRICULA":
                    self.curriculas[data[0]]=[data[i] for i in range(1,len(data))]
        self.days=self.confs['days']
        self.periods_per_day=self.confs['periods']
        self.semesters=self.confs['semesters']
        self.final_years=self.confs['final_year']
        
        for assignment_lecturer,assignment_info in self.assignments.items():
            for course,_,lectures,lecture_type in assignment_info:
                if lecture_type=='th':
                    for lecture_id in range(lectures):
                        self.events.append((course,lecture_id,assignment_lecturer))
                