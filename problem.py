import os
import networkx as nx
from collections import defaultdict
from tabulate import tabulate
import unicodedata as ud
import random,pandas as pd
import logging
import numpy as np
from itertools import combinations

class Course:
    UNICODET={ord('\N{COMBINING ACUTE ACCENT}'):None}

    def __init__(self,cid,cname,csemester,ctheory_hours,ctutoring_hours,clab_hours,ccredits,clab_hours_in_use):
        self.id=cid
        self.name=str(cname)
        self.name=ud.normalize('NFD',self.name).translate(Course.UNICODET).upper()
        self.semester=csemester
        self.theory_hours=ctheory_hours
        self.tutoring_hours=ctutoring_hours
        self.lab_hours=clab_hours
        self.credits=ccredits
        self.lab_hours_in_use=clab_hours_in_use
        self.laboratory_events=1
    
    def assign_periods(self,total_hours=1):
        self.lab_hours_in_use+=total_hours

    def assert_valid(self):
        assert(self.lab_hours_in_use==self.lab_hours)    

    def get_type(self,lecture_id):
        if  lecture_id<self.theory_hours:
            return f"{lecture_id},ΘΕΩΡΙΑ"
        elif lecture_id<=self.theory_hours+self.tutoring_hours:
            return f"{lecture_id},ΦΡΟΝΤΗΣΤΗΡΙΟ"
        return f"{lecture_id},ΕΡΓΑΣΤΗΡΙΟ"     
    
    def begin_theory(self):
        return 0

    def lab_start_index(self):
        return self.begin_lab()+self.lab_hours_in_use

    def end_theory(self):
        return self.theory_hours

    def begin_tutoring(self):
        return self.theory_hours
    
    def end_tutoring(self):
        return self.theory_hours+self.tutoring_hours

    def begin_lab(self):
        return self.theory_hours+self.tutoring_hours

    def compatibility(self,lecture_type,total_lectures):
        if lecture_type=="th":
            print(f"Compitable:={total_lectures==self.theory_hours}({total_lectures}/{self.theory_hours})")
        elif lecture_type=="tut":
            print(f"Compitable:={total_lectures==self.tutoring_hours}({total_lectures}/{self.tutoring_hours})")
        else:
            return

    # equality based on a given name    
    def __eq__(self,objname):
        if objname.startswith(f"NAME:"):
            return self.name==objname.removeprefix("NAME:")
        elif objname.startswith(f"ID:"):
            return self.id==str(objname).removeprefix("ID:")
        else:
            return self.name==objname

class Lecturer:
    def __init__(self,lname,lemail,lid):
        self.name=lname
        self.email=lemail
        self.id=lid
        self.events=defaultdict(list)
        self.number_of_labs=0
        self.period_restrictions=None
    
    def number_of_events(self):
        return len(self.events)
    
    def __IADD__(self,assignment):
        course,lectures,hours_per_lecture,lecture_type=assignment[0],assignment[1],assignment[2],assignment[3]
        if lecture_type=='l':
            for lecture_id in range(lectures*hours_per_lecture):
                self.events[course].append(lecture_id)
            self.number_of_labs+=1
        else:
            for lecture_id in range(lectures):
                self.events[course].append(lecture_id)

    def unavailabilities_generator(self,number_of_periods):
        self.period_restrictions=pd.DataFrame()
        self.period_restrictions.columns=[f'P{i}' for i in range(number_of_periods)]
        periods=list(range(number_of_periods))
        while True:
            for col in self.period_restrictions.columns.to_list():
                self.period_restrictions[col]=random.choices([0,1],[0.75,0.25])
            
            if self.period_restrictions.sum(axis=1)<self.number_of_events():
                if [True for period1,period2 in zip(periods[:-1],periods[1:]) if self.period_restrictions.loc[:,[f'P{period1}',f'P{period2}']].sum(axis=1)==0].count(True)>self.number_of_labs():
                    break
    
    def __eq__(self,other_name) -> bool:
        return self.name==other_name

    def __str__(self):
          return f'Name:{self.name}\nEmail:{self.email}\nId:{self.id}\nEvents:{self.events}\nRestrictions\n{self.period_restrictions.to_string(index=False)}'   

class Problem:  
    path_to_datasets=os.path.join('','Datasets','dit_datasets','dit_winter_pregraduate.txt')
    path_to_sample=os.path.join('','Datasets','dit_datasets','dit_winter_small_dataset.txt')
    @staticmethod
    def change_path_to_dataset(new_path_to_dataset):
        Problem.path_to_datasets=new_path_to_dataset

    def init_parameters(self):
        self.courses=list()
        self.rooms=list()
        self.lecturers=defaultdict(list)
        self.curriculas=defaultdict(list)
        self.events=list()
        self.event_lecturers=defaultdict(list)
        self.lecturer_events=defaultdict(list)
        self.room_unavailabilities=None
        self.period_unavailabilities=None
        self.lecturer_unavailabilities=None
        self.assignments=defaultdict(list)
        self.consecutive_theories=list()
        self.consecutive_tutoring=list()
        self.consecutive_labs=list()
        self.consecutive_events=nx.Graph()
    
    def event_identifier(self,course,lecture):
        for index,(course_id,lecture_id,_,_) in enumerate(self.events):
            if course_id==course and lecture_id==lecture:
                return index
        raise IndexError(f'Value ({course},{lecture}) does not exist')

    def logger(self):
        _logger=logging.getLogger(name=f'Problem_dit_logger')
        _logger.setLevel(logging.DEBUG)
        formatter=logging.Formatter("%(asctime)s\t%(message)s")
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        _logger.addHandler(sh)
        return _logger
        

    def course_assignment(self,verbose=False):
        if verbose:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

        for assignment_lecturer,assignment_info in self.assignments.items():
            for course,lectures,hours_per_lecture,lecture_type in assignment_info:
                # self.log.info(f'{course} {lectures} {hours_per_lecture} {lecture_type}')
                if lecture_type=='th':
                    total_theory_periods=hours_per_lecture*lectures
                    event_group=[(course,lecture_id,assignment_lecturer,lecture_type) for lecture_id in range(total_theory_periods)]
                    self.events.extend(event_group)
                    self.log.debug(f'(Course {course},Lectures:{lectures}): Lecturer:{assignment_lecturer}, type:{lecture_type}\tTotal events created:{len(event_group)}')
                    self.courses[self.courses.index(course)].compatibility(lecture_type,total_theory_periods)
                
                elif lecture_type=='tut':
                    total_tutoring_periods=hours_per_lecture*lectures
                    event_group=[(course,lecture_id,assignment_lecturer,lecture_type) for lecture_id in range(self.courses[self.courses.index(course)].begin_tutoring(),self.courses[self.courses.index(course)].begin_tutoring()+(total_tutoring_periods))]
                    self.events.extend(event_group)
                    self.log.debug(f'(Course {course},Lectures:{lectures}): Lecturer:{assignment_lecturer}, type:{lecture_type}\tTotal events created:{len(event_group)}')
                elif lecture_type=='l':
                    lecturer_lab_periods=hours_per_lecture*lectures
                    self.events.extend([(course,lecture_id,assignment_lecturer,lecture_type) for lecture_id in range(self.courses[self.courses.index(course)].lab_start_index(),self.courses[self.courses.index(course)].lab_start_index()+lecturer_lab_periods)])
                    if hours_per_lecture!=1:
                        for lecture_id in range(self.courses[self.courses.index(course)].lab_start_index(),self.courses[self.courses.index(course)].lab_start_index()+lecturer_lab_periods,hours_per_lecture):
                            for lecture_id2 in range(lecture_id,lecture_id+hours_per_lecture-1):
                                self.consecutive_events.add_edge(self.event_identifier(course,lecture_id2),self.event_identifier(course,lecture_id2+1))
                        self.courses[self.courses.index(course)].assign_periods(lecturer_lab_periods)
                        self.log.info(f'Lecturer {assignment_lecturer} assigned in {lecturer_lab_periods} periods=>{lecturer_lab_periods}')

    def __init__(self):
        self.G=nx.Graph()
        self.init_parameters()
        self.log=self.logger()
        category=None
        confs=dict()
        with open(Problem.path_to_datasets,'r',encoding='utf8') as RF:
            for i,line in enumerate(RF):
                line=line.strip()
                if i<6:
                    data=line.split(':')
                    confs[data[0].replace(':','').strip()]=data[1]
                    continue
            
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
                    self.courses.append(Course(data[0].strip(),data[1].strip().upper(),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6]),0))
                elif category=="LECTURERS":
                    self.lecturers.append(Lecturer(data[0].strip(),data[1].strip(),data[2].strip()))
                elif category=="ROOMS":
                    self.rooms.append(tuple(data))
                elif category=="ASSIGNMENTS":
                    self.assignments[ud.normalize('NFD',data[1]).translate(Course.UNICODET).strip().upper()].append((ud.normalize('NFD',data[0]).translate(Course.UNICODET).upper(),int(data[2]),int(data[3]),data[4]))
                elif category=="CURRICULA":
                    self.curriculas[data[0].strip().upper()]=[ud.normalize('NFD',data[0]).translate(Course.UNICODET).upper() for i in range(1,len(data))]

        self.days=int(confs['days'])
        self.periods_per_day=int(confs['periods'])
        self.semesters=int(confs['semesters'])
        self.final_years=confs['final_year']

        self.course_assignment(verbose=True)
        
        # decode events per lecturer
        for event_id,(course,lecture_id,assignment_lecturer,_) in enumerate(self.events):
            assignment_lecturer=ud.normalize('NFD',assignment_lecturer).translate(Course.UNICODET).strip().upper()
            self.lecturer_events[assignment_lecturer].append(event_id)
            self.event_lecturers[event_id].append(assignment_lecturer)
        
        self.create_graph()

    def unavailabilities(self,random=False,path=''):
        if random==True and path!='':
            raise ValueError("Can not sampling the unavailabilities and read them from file")
        
        if random:
            self.room_unavailabilities=self.random_room_unavailabilities()
            self.period_unavailabilities=self.random_period_unavailabilities()
            self.lecturer_unavailabilities=self.random_lecturer_unavailabilities()
        else:
            pass

    def number_of_courses(self):
        return len(self.courses)
    
    def number_of_rooms(self):
        return len(self.rooms)

    def number_of_curriculas(self):
        return len(self.curriculas)

    def number_of_events(self):
        return len(self.events)
    
    def number_of_lecturers(self):
        return len(self.lecturer_events.keys())
    
    def number_of_periods(self):
        return self.days*self.periods_per_day
            
    def create_graph(self):
        self.G=nx.Graph()
        self.G.add_nodes_from(list(range(len(self.events))))
        for i,(course,lecture,lecturer,lecture_type) in enumerate(self.events):
            for j,(course2,lecture2,lecturer2,lecture_type2) in enumerate(self.events):
                if i==j: continue
                elif course==course2 and lecture_type==lecture_type2 and (lecture_type=='th' or lecture_type=='tut'):
                    self.G.add_edge(i,j)
                elif course==course2 and ((lecture_type=='l' and lecture_type2=='th') or (lecture_type=='th' and lecture_type2=='l') or (lecture_type=='tut' and lecture_type2=='l') or (lecture_type=='l' and lecture_type2=='tut')):
                    self.G.add_edge(i,j)

        for _,lecturer_events in self.lecturer_events.items():
            for index1 in range(len(lecturer_events)):
                for index2 in range(index1+1,len(lecturer_events)):
                    self.G.add_edge(lecturer_events[index1],lecturer_events[index2])        

    def info(self):
        print("-"*5+" Problem "+"-"*5)
        print(nx.info(self.G))
        print(f"Density:{nx.density(self.G)}")
        print(f'Teachers workload:{self.teachers_workload()}')
        print(f'Room unavailability:{self.room_suitability()}')
        print(f'Mean Teacher\'s unavailability:{self.teachers_unavailability()}')

    def per_lecturer(self):
        for lecturer,levents in self.lecturer_events.items():
            rows=[]
            print(f'Lecturer:{lecturer}\n'+'-'*10)
            for event_id in levents:
                rows.append([self.events[event_id][0],self.courses[self.courses.index(self.events[event_id][0])].get_type(self.events[event_id][1])])        
            print(tabulate(rows,headers=['Course name','Lecture type'],tablefmt='fancy_grid'),end='\n\n')

    def conflict_density(self):
        return self.G.number_of_edges()*2/self.number_of_events()**2
        # return nx.density(self.G)

    def teachers_workload(self):
        return sum([len(lecturer_events) for _,lecturer_events in self.lecturer_events.items()])/self.number_of_lecturers()

    def room_suitability(self):
        return sum([self.room_unavailabilities[column] for column in [f'R{i+1}' for i in range(self.number_of_rooms())]])
    
    def teachers_unavailability(self):
        return sum([self.period_unavailabilities[column].sum() for column in [f'P{i+1}' for i in range(self.number_of_periods())]])/self.number_of_lecturers()
    
    def random_lecturer_unavailabilities(self):
        rows=[]
        headers=['LECTURER']+[f'P{i+1}' for i in range(self.P)]
        for lecturer_name,_ in self.lecturer_events.items():
            rows.append([lecturer_name]+[random.randint(0,1) for _ in range(self.P)])
        return pd.DataFrame(rows,columns=headers)

    def random_period_unavailabilities(self):
        rows=[]
        headers=['COURSE']+[f'P{i+1}' for i in range(self.P)]
        for course in self.courses:
            unavailabilities=[random.randint(0,1) for _ in range(self.P)]
            while sum(unavailabilities)==0:
                unavailabilities=[random.randint(0,1) for _ in range(self.P)]
            rows.append([course.name]+unavailabilities)
        return pd.DataFrame(rows,columns=headers)

    def random_room_unavailabilities(self):
        rows=[]
        headers=['COURSE']+[f'R{i+1}' for i in range(self.R)]
        for event in self.events:
            if event[3]=='th':
                room_availabilities=[random.randint(0,1) if self.rooms[i][1]=="ΑΜΦΙΘΕΑΤΡΟ" else 0  for i in range(self.R)]
            elif  event[3]=='l': 
                room_availabilities=[random.randint(0,1) if self.rooms[i][1]=="ΕΡΓΑΣΤΗΡΙΟ" else 0 for i in range(self.R)]
            else:
                room_availabilities=[random.randint(0,1) for i in range(self.R)]
            while sum(room_availabilities)==0:
                if event[3]=='th':
                    room_availabilities=[random.randint(0,1) if self.rooms[i][1]=="ΑΜΦΙΘΕΑΤΡΟ" else 0  for i in range(self.R)]
                elif  event[3]=='l': 
                    room_availabilities=[random.randint(0,1) if self.rooms[i][1]=="ΕΡΓΑΣΤΗΡΙΟ" else 0 for i in range(self.R)]
                else:
                    room_availabilities=[random.randint(0,1) for i in range(self.R)]
            rows.append([event[0]]+room_availabilities)
        return pd.DataFrame(rows,columns=headers)

def scenario1():
    # Generate unavailabilities and problem info.
    problem=Problem()
    problem.unavailabilities(random=True)
    writer=pd.ExcelWriter(path=os.path.join('','Datasets','dit_datasets','period_unavailabilities.xlsx'),mode='w')
    problem.period_unavailabilities.to_excel(excel_writer=writer)
    writer.close()
    del writer

    writer=pd.ExcelWriter(path=os.path.join('','Datasets','dit_datasets','room_unavailabilities.xlsx'),mode='w')
    problem.room_unavailabilities.to_excel(excel_writer=writer)
    writer.close()
    del writer

    writer=pd.ExcelWriter(path=os.path.join('','Datasets','dit_datasets','lecturer_unavailabilities.xlsx'),mode='w')
    problem.lecturer_unavailabilities.to_excel(excel_writer=writer)
    writer.close()
    del writer

    problem.info()

def scenario2():
    problem=Problem()
    problem.per_lecturer()


if __name__=='__main__':
    # scenario1() # Create problem unavailabilities
    scenario2() # Produce problem graph