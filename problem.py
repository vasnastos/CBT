import os
import networkx as nx
from collections import defaultdict
from tabulate import tabulate
import unicodedata as ud
import random,pandas as pd

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
    
    def assign_lecture(self,total_hours=1):
        self.lab_hours_in_use+=total_hours

    def assert_valid(self):
        assert(self.lab_hours_in_use==self.lab_hours)    

    def get_type(self,lecture_id):
        if  lecture_id<self.theory_hours:
            return f"{lecture_id},ΘΕΩΡΙΑ"
        elif lecture_id<=self.theory_hours+self.tutoring_hours:
            return f"{lecture_id},ΕΝΙΣΧΥΤΙΚΟ"
        return f"{lecture_id},ΕΡΓΑΣΤΗΡΙΟ"     

    def set_total_lab_hours(self,lab_events):
        self.laboratory_events=lab_events

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
    
    def __eq__(self,objname):
        return self.name==objname


class Problem:  
    path_to_datasets=os.path.join('','Datasets','dit_datasets','dit_winter_pregraduate.txt')
    path_to_sample=os.path.join('','Datasets','dit_datasets','dit_winter_small_dataset.txt')
    @staticmethod
    def change_path_to_dataset(new_path_to_dataset):
        Problem.path_to_datasets=new_path_to_dataset

    def init_parameters(self):
        self.confs=dict()
        self.courses=list()
        self.rooms=list()
        self.lecturers=defaultdict(list)
        self.curriculas=defaultdict(list)
        self.events=list()
        self.event_lecturers=defaultdict(list)
        self.lecturer_events=defaultdict(list)
        self.room_unavailabilities=defaultdict(list)
        self.period_unavalabilities=defaultdict(list)
        self.assignments=defaultdict(list)
    
    def __init__(self):
        self.G=nx.Graph()
        self.init_parameters()

        category=None
        with open(Problem.path_to_datasets,'r',encoding='utf8') as RF:
        # with open(Problem.path_to_sample,'r',encoding='utf8') as RF:
            for i,line in enumerate(RF):
                line=line.strip()
                if i<6:
                    data=line.split(':')
                    self.confs[data[0].replace(':','').strip()]=data[1]
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
                    self.lecturers[data[0]]={"email":data[1],"username":data[2],"courses":list()}
                elif category=="ROOMS":
                    self.rooms.append(tuple(data))
                elif category=="ASSIGNMENTS":
                    self.assignments[ud.normalize('NFD',data[1]).translate(Course.UNICODET).strip().upper()].append((ud.normalize('NFD',data[0]).translate(Course.UNICODET).upper(),int(data[2]),int(data[3]),data[4]))
                elif category=="CURRICULA":
                    self.curriculas[data[0].strip().upper()]=[ud.normalize('NFD',data[0]).translate(Course.UNICODET).upper() for i in range(1,len(data))]

        self.days=int(self.confs['days'])
        self.periods_per_day=int(self.confs['periods'])
        self.semesters=int(self.confs['semesters'])
        self.final_years=self.confs['final_year']
        self.P=self.days*self.periods_per_day
        self.R=len(self.rooms)
        for assignment_lecturer,assignment_info in self.assignments.items():
            for course,hours_per_lecture,lectures,lecture_type in assignment_info:
                if lecture_type=='th':
                    for lecture_id in range(hours_per_lecture*lectures):
                        self.events.append((course,lecture_id,assignment_lecturer,lecture_type))
                elif lecture_type=='tut':
                    for lecture_id in range(self.courses[self.courses.index(course)].begin(),self.courses[self.courses.index(course)].begin()+(hours_per_lecture*lectures)):
                        self.events.append((course,lecture_id,assignment_lecturer,lecture_type))
                elif lecture_type=="l":
                    total_lecturer_lab_hours=hours_per_lecture*lectures
                    for lecture_id in range(self.courses[self.courses.index(course)].begin_lab()+self.courses[self.courses.index(course)].lab_hours_in_use,self.courses[self.courses.index(course)].begin_lab()+self.courses[self.courses.index(course)].lab_hours_in_use+total_lecturer_lab_hours+1):
                        self.events.append((course,lecture_id,assignment_lecturer,lecture_type))
                    self.courses[self.courses.index(course)].assign_lecture(total_lecturer_lab_hours+1)
        
        # decode events per lecturer
        for event_id,(course,lecture_id,assignment_lecturer,assignment_type) in enumerate(self.events):
            self.lecturer_events[assignment_lecturer.upper()].append(event_id)
            self.event_lecturers[event_id].append(assignment_lecturer.upper())
        
        self.create_graph()
                        
    def number_of_courses(self):
        return len(self.courses)
    
    def number_of_rooms(self):
        return len(self.rooms)

    def number_of_curriculas(self):
        return len(self.curriculas)

    def number_of_events(self):
        return len(self.events)
            
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
        
        print(self.lecturer_events)
        for _,lecturer_events in self.lecturer_events.items():
            for index1 in range(len(lecturer_events)):
                for index2 in range(index1+1,len(lecturer_events)):
                    self.G.add_edge(lecturer_events[index1],lecturer_events[index2])
        
        print(nx.info(self.G))
        print(f"Density:{nx.density(self.G)}")
    
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
        pass

    def room_suitability(self):
        pass
    
    def teachers_unavailability(self):
        pass
    
    def random_period_unavailabilities(self):
        rows=[]
        headers=['LECTURER']+[f'P{i+1}' for i in range(self.P)]
        for lecturer_name,_ in self.lecturer_events.items():
            rows.append([lecturer_name]+[random.randint(0,1) for _ in range(self.P)])
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
           
if __name__=='__main__':
    problem=Problem()
    writer=pd.ExcelWriter(path=os.path.join('','Datasets','dit_datasets','period_unavailabilities.xlsx'),mode='w')
    problem.random_room_unavailabilities().to_excel(excel_writer=writer)
    writer.close()
    del writer

    writer=pd.ExcelWriter(path=os.path.join('','Datasets','dit_datasets','room_unavailabilities.xlsx'),mode='w')
    problem.random_room_unavailabilities().to_excel(excel_writer=writer)
    writer.close()
    del writer

# 1. Προσθήκη καταννεμημένων και παράλληλων συστημάτων
# 2. Δημιουργία σελίδας αντιστοίχισης μαθημάτων
# 3. Δημιουργία μοντέλου αρχικής λύσης