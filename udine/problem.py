from itertools import combinations,product
import os
from collections import defaultdict
from udine.core import Course,Room
from tabulate import tabulate
import networkx as nx

class Problem:
    path_to_datasets=os.path.join('','Datasets','udine_datasets')
    def __init__(self):
        self.name=None
        self.courses=dict()
        self.curriculas=defaultdict(list)
        self.lecturers=dict()
        self.rooms=dict()
        self.lectures=dict()
        self.room_numeric_id=dict()
    
    def reset(self):
        self.name=None
        self.courses.clear()
        self.curriculas.clear()
        self.lecturers.clear()
        self.rooms.clear()
        self.lectures.clear()
        self.room_numeric_id.clear()

    def read_instance(self,ds_name):
        label=''
        room_counter=0
        self.reset()

        with open(os.path.join(Problem.path_to_datasets,ds_name),'r') as RF:
            cfg=dict()
            for i,line in enumerate(RF):
                if i<9:
                    key,value=[x for x in line.split()]
                    cfg[key.replace(':','').strip()]=value                

                if len(line.strip())==0: continue 
                elif line=='\n': continue
                elif line.strip()=='COURSES:':
                    label='COURSES'
                    continue
                elif line.strip()=='ROOMS:':
                    label='ROOMS'
                    continue
                elif line.strip()=='CURRICULA:':
                    label='CURRICULA'
                    continue
                elif line.strip()=='UNAVAILABILITY_CONSTRAINTS:':
                    label='UNAVAILABILITY_CONSTRAINTS'
                    continue
                elif line.strip()=='ROOM_CONSTRAINTS:':
                    label='ROOM_CONSTRAINTS'
                    continue
                elif line=='END.':
                    break
                
                data=line.split()
                if label=='COURSES':
                    self.courses[int(data[0].replace('c','').strip())]=Course(int(data[1].replace('t','').strip()),int(data[2].strip()),int(data[3].strip()),int(data[4].strip()),int(data[5].strip()))
                elif label=='ROOMS':
                    self.rooms[room_counter]=Room(data[0].strip(),int(data[1].strip()),int(data[2].strip()))
                    self.room_numeric_id[data[0].strip()]=room_counter
                    room_counter+=1
                elif label=='CURRICULA':
                    for course_index in range(2,len(data)):
                        self.curriculas[int(data[0].replace('t','').strip())].append(int(data[course_index].replace('t','').strip()))
                elif label=='UNAVAILABILITY_CONSTRAINTS':
                    day,period=int(data[1].strip()),int(data[2].strip())
                    self.courses[int(data[0].replace('c','').strip())].add_constraint(day*self.periods_per_day+period)
                elif label=='ROOM_CONSTRAINTS':
                    course_id,room_id=int(data[0].replace('c','').strip()),int(data[1].strip())
                    self.courses[course_id].add_room_constraint(self.room_numeric_id[room_id])

            self.name=cfg['Name']
            self.num_courses=int(cfg['Courses'].replace(':','').strip())
            self.num_rooms=int(cfg['Room'].replace(':','').strip())
            self.days=int(cfg['Days'].replace(':','').strip())
            self.periods_per_day=int(cfg['Periods_per_day'].replace(':','').strip())
            self.num_curriculas=int(cfg['Curricula'].replace(':','').strip())
            self.min_daily_courses,self.max_daily_lectures=[int(x.strip()) for x in cfg['Min_Max_Daily_Lectures'].replace(':','').strip().split()]
            self.num_unavailability_constraints=int(cfg['UnavailabilityConstraints'].replace(':','').strip())
            self.num_room_constraints=int(cfg['RoomConstraints'].replace(':','').strip())
            self.num_periods=self.days*self.periods_per_day
            self.lectures=[(course_id,lecture_id) for course_id in range(self.num_courses) for lecture_id in range(self.courses[course_id])]
            self.number_of_lectures=len(self.lectures)

    def find_curricula(self,course_id):
        return [curricula_id for curricula_id in range(self.num_curriculas) if course_id in self.curriculas[curricula_id]][0]
    
    def conflict_density(self):
        return sum([len(list(product(*[range(self.curriculas[curricula_id][course_index1]),range(self.curriculas[curricula_id][course_index2])])))*2 for curricula_id in range(self.num_curriculas) for course_index1 in range(len(self.curriculas[curricula_id])) for course_index2 in range(course_index1+1,len(self.curriculas[curricula_id]))])/self.number_of_lectures**2

    def teachers_availability(self):
        return len([(lecture_id,period_id) for course_id in range(self.num_courses) for lecture_id in range(self.courses[course_id].lectures) for period_id in range(self.num_periods) if period_id not in self.courses[course_id].unavailability_constraints])/self.number_of_lectures*self.num_periods

    def room_suitability(self):
        return len([(lecture_id,room_id) for course_id in range(self.num_courses) for lecture_id in range(self.courses[course_id].lectures) for room_id in range(self.num_rooms) if room_id not in self.courses[course_id].unavailability_constraints])

    def lectures_per_day_per_curriculum(self):
        return sum([(lecture_id,period_id) for course_id in range(self.num_courses) for lecture_id in range(self.courses[course_id].lectures) for period_id in range(self.num_periods) if period_id not in self.courses[course_id].unavailability_constraints])/(self.number_of_lectures*self.days)

    def room_occupation(self):
        return self.number_of_lectures/len([(room_id,period_id) for room_id in range(self.num_rooms) for period_id in range(self.num_periods)])

    def __str__(self):
        return str(tabulate([['Dataset',self.name],['Courses',self.num_courses],['Rooms',self.num_rooms],['Days',self.days],['Periods per day',self.periods_per_day],['Curriculas',self.num_curriculas],['Min Daily Lectures',self.min_daily_courses],['Max Daily lectures',self.max_daily_lectures],['Period Constrains', self.num_unavailability_constraints],['Room Constraints',self.num_room_constraints]],headers=['Formulation','Value']))
