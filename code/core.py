import os,pandas as pd

from dit import Course as DC,Lecturer as DL,Classroom as DCL,Curricula as DCR
from udine import Lecturer,Course,Classroom,Curricula,Meeting
from collections import namedtuple
from itertools import product
from tabulate import tabulate
import networkx as nx


class Importer:
    path_to_dit_courses=os.path.join('..','Datasets','dit_fall','dit_courses.xlsx')
    path_to_dit_classes=os.path.join('..','Datasets','dit_fall','dit_classrooms.xlsx')
    path_to_dit_lecturers=os.path.join('..','Datasets','dit_fall','teachers.csv')
    path_to_dit_curricula=os.path.join('..','Datasets','dit_fall')

    path_to_udine_datasets=os.path.join('..','Datasets','udine_datasets')

    udine_datasets=[
        'Udine1.ectt',
        'Udine2.ectt',
        'Udine3.ectt',
        'Udine4.ectt',
        'Udine5.ectt'
    ]

    @staticmethod
    def load_udine_dataset(pandas=False,udine_dataset_name=None,create_instance=False):
        extra_info=dict()
        courses,rooms,lecturers,curricula,unavailability_constraints,room_constraints,meetings=list(),list(),list(),list(),list(),list(),list()
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
                elif line.strip()=="CURRICULA:":
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
                        courses.append(Course(data[0].strip(),data[1].strip(),int(data[2].strip()),int(data[3].strip()),int(data[4].strip()),int(data[5].strip())))
                    
                    if data[1].strip() not in lecturers:
                        lecturers.append(Lecturer(data[1].strip()))
                    
                    lecturers[lecturers.index(data[1].strip())].add_course(courses[courses.index(data[0].strip())])
                
                elif category=="ROOMS":
                    if data[0].strip() not in rooms:
                        rooms.append(Classroom(data[0].strip(),int(data[1].strip()),int(data[2].strip())))
                
                elif category=="CURRICULA":
                    if data[0].strip() not in curricula:
                        curricula.append(Curricula(data[0].strip()))
                        
                    for i in range(2,len(data)):
                        curricula[curricula.index(data[0].strip())].add_course(courses[courses.index(data[i])])
                        courses[courses.index(data[i].strip())].curricula=data[0].strip()

                elif category=="UNAVAILABILITY_CONSTRAINTS":
                    unavailability_constraints.append(Course_constraint._make(data))
                
                elif category=="ROOM_CONSTRAINT":
                    room_constraints.append(Room_constraint._make(data))
        
        # Create meetings for each lesson
        for course in courses:
            for _ in range(course.lectures):
                meeting_obj=Meeting(course.get_lecture_id(),course.course_id)

                for course_id,day,period in unavailability_constraints:
                  if course_id==meeting_obj.course:
                      meeting_obj.add_constraint((day,period))
                for course_id,room_id in room_constraints:
                    meeting_obj.add_constraint(room_id,constraint_for='room')
                
                meeting_lecturer=courses[courses.index(course.course_id)].lecturer
                meeting_curricula=courses[courses.index(course.course_id)].curricula

                meeting_obj.lecturer=lecturers[lecturers.index(meeting_lecturer)]
                meeting_obj.curricula=meeting_curricula

                meetings.append(meeting_obj)

        # Work with dataframes
        if pandas:
            courses=pd.DataFrame(data=[list(course) for course in courses],columns=['ID','LECTURER',"#LECTURERS","#DISTINCT_PERIODS","STUDENTS"])
            lecturers=pd.DataFrame(data=[list(lecturer) for lecturer in lecturers],columns=['ID','COURSES'])
            classrooms=pd.DataFrame(data=[list(classr) for classr in classrooms],columns=['ID','CAPACITY','BUILDING_ID'])
            curricula=pd.DataFrame(data=[list(c) for c in curricula],columns=['ID','CURRICULA'])
            meetings=pd.DataFrame(data=[list(meeting) for meeting in meetings],columns=["ID","COURSE","DAY","PERIOD OF DAY","UNAVAILABILITY_CONSTRAINTS","ROOM_CONSTRAINTS"])
        
        return (courses,lecturers,rooms,curricula,meetings,extra_info) if not create_instance else  Problem.init_instance(udine_dataset_name,courses,lecturers,rooms,curricula,meetings,extra_info)

    @staticmethod
    def load_dit_dataset(dataset_name,pandas=False):
        #WIP
        pass

class Problem:
    def __init__(self,dataset_name,pandas=False,init_vars=True):
        self.courses,self.lecturers,self.classrooms,self.curricula,self.meetings,extra_information=list(),list(),list(),list(),list(),dict()
        self.problem_id=dataset_name

        if init_vars:
            self.courses,self.lecturers,self.classrooms,self.curricula,self.meetings,extra_information=Importer.load_udine_dataset(dataset_name,pandas)
            self.days,self.periods_per_day=extra_information.get('Days',-1),extra_information.get('Periods_per_day',-1)
            self.periods={(i,j):list()  for i in range(self.days) for j in range(self.periods_per_day)}
            self.number_of_meetings=len(self.meetings)
            self.p=len(self.periods)
            self.C=len(self.courses)
            self.T=len(self.lecturers)
            self.R=len(self.classrooms)
            self.CR=len(self.curricula)
            self.available_periods=list(product(range(self.days),range(self.periods_per_day)))


        else:
            self.days,self.periods_per_day=-1,-1
            self.periods={}
            self.number_of_meetings=-1
            self.P=-1
            self.C=-1
            self.T=-1
            self.R=-1
            self.CR=-1
            self.available_periods=list()


    @classmethod
    def init_instance(cls,dataset_name,courses,lecturers,classrooms,curricula,meetings,extra_information):
        problem=cls(dataset_name,init_vars=False)
        problem.courses=courses
        problem.lecturers=lecturers
        problem.classrooms=classrooms
        problem.curricula=curricula
        problem.meetings=meetings
        problem.extra_information=extra_information
        problem.days,problem.periods_per_day=int(extra_information.get('Days',-1)),int(extra_information.get('Periods_per_day',-1))
        problem.periods={(i,j):list()  for i in range(problem.days) for j in range(problem.periods_per_day)}
        problem.number_of_meetings=len(problem.meetings)
        problem.P=problem.days * problem.periods_per_day
        problem.C=len(problem.courses)
        problem.R=len(problem.classrooms)
        problem.CR=len(problem.curricula)
        return problem

    def confict_density(self):
        cd_meetings=set()
        # Meetings which are done be the same lecturer
        for lecturer in self.lecturers:
            for course in lecturer.courses:
                cd_meetings.add((course.course_id,course.lectures))

        for curricula_obj in self.curricula:
            for course in curricula_obj.courses:
                cd_meetings.add((course.course_id,course.lectures))

        cd_meetings=list(cd_meetings)
        return sum([nlectures for _,nlectures in cd_meetings])/self.number_of_meetings   

    def teachers_availability(self):
        # ta=0
        # for meeting in self.meetings:
        #     for period_pair in self.available_periods:
        #         if meeting.is_feasible(period_pair):
        #             ta+=1
        # return ta/self.T
        return sum([1 for meeting in self.meetings for period_pair in self.available_periods if meeting.is_feasible(period_pair)])/self.T
    
    def room_suitability(self):
        # rs=0
        # for meeting in self.meetings:
        #     for room in self.classrooms:
        #         if meeting.is_feasible(room.room_id,feasibility_for='room'):
        #             rs+=1
        # return rs/self.R
        return sum([1 for meeting in self.meetings for room in self.classrooms if meeting.is_feasible(room.room_id,feasibility_for='room')])

    def find_curricula(self,course_id):
        for i,curricula_obj in enumerate(self.curricula):
            if curricula_obj.is_curricula_of(course_id):
                return i
        return -1

    def lectures_per_day_per_curriculum(self):
        return self.number_of_meetings/(self.days)
    
    def room_occupation(self):
        return self.number_of_meetings/len([(room.room_id,period_pair) for room in self.classrooms for period_pair in list(self.periods.keys())])

    # Validators
    def curricula_validance(self):
        for curricula_obj in self.curricula:
            for course in curricula_obj.courses:
                for course_2 in self.curricula_obj.courses:
                    period1=self.speriods.get(course,-1)
                    period2=self.speriods.get(course_2,-1)
                    if period1==-1 or period2==-1: continue
                    if period1==period2:
                        return False
        return True
    
    def describe(self):
        for lecturer in self.lecturers:
            lecturer._tabulate_()
        
        print('Curricala information')
        for curricula_obj in self.curricula:
            curricula_obj._tabulate_()

    # Create graph
    def find_neighbors(self,mid):
        return [self.meetings[j].meeting_id for j in range(mid+1,self.number_of_meetings) if self.meetings[mid].is_neighbor_meeting(self.meetings[j]) and j!=mid]

    def create_graph(self):
        self.G=nx.Graph()
        self.G.add_nodes([meeting.meeting_id for meeting in self.meetings]) 
        for index,meeting in enumerate(self.meetings):
            neighbors=self.find_neighbors(index)
            for neighbor in neighbors:
                self.G.add_edge(meeting.meeting_id,neighbor)

    def validance(self):
        #check courses validance
        pass


def select_dataset():
    for index,ds_name in enumerate(Importer.udine_datasets):
        print(f'{index+1}.{ds_name}')
    ds_index=int(input('Select dataset index:'))
    return Importer.udine_datasets[ds_index-1]


if __name__=='__main__':
    selected_dataset_name=select_dataset()
    problem=Importer.load_udine_dataset(udine_dataset_name=selected_dataset_name,create_instance=True)
    problem.describe()