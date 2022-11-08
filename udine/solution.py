from udine.problem import Problem
import os

class Solution:
    path_to_solution=os.path.join('','solutions')
    def __init__(self,ds_name:str):
        self.problem=Problem()
        self.problem.read_instance(ds_name)
        self.solution_per_room={room_id:list() for room_id in range(self.problem.num_rooms)}
        self.solution_per_period={period_id:list() for period_id in range(self.problem.num_periods)}
        self.course_solution=dict()
        self.id=ds_name.replace('','ectt')
    
    def schedule(self,course_id,lecture_id,room_id,period_id):
        self.course_solution[(course_id,lecture_id)]=(period_id,room_id)
        self.solution_per_period[period_id].append((course_id,lecture_id))
        self.solution_per_room[room_id].append((course_id,lecture_id))

    def unschedule(self,course_id,lecture_id):
        self.solution_per_period[self.course_solution[(course_id,lecture_id)][0]].remove((course_id,lecture_id))
        self.solution_per_room[self.course_solution[(course_id,lecture_id)][1]].remove((course_id,lecture_id))
        self.course_solution[(course_id,lecture_id)]=(-1,-1)
    
    def is_isolated_lecture(self,course_id,lecture_id)->bool:
        day=self.course_solution[(course_id,lecture_id)][0]//self.problem.periods_per_day
        previous_period=self.course_solution[(course_id,lecture_id)][0]-1
        next_period=self.course_solution[(course_id,lecture_id)][0]+1
        course_curricula=self.problem.find_curricula(course_id)
        if previous_period<day*self.problem.periods_per_day:
            if len([(course_id2,lecture_id2) for course_id2 in self.problem.curriculas[course_curricula] for lecture_id2 in range(self.problem.courses[course_id2]) if self.course_solution[(course_id2,lecture_id2)][0]==previous_period])==0:
                return True
            return False
        elif next_period==day*self.problem.periods_per_day+self.problem.periods_per_day:
            if len([(course_id2,lecture_id2) for course_id2 in self.problem.curriculas[course_curricula] for lecture_id2 in range(self.problem.courses[course_id2]) if self.course_solution[(course_id2,lecture_id2)][0]==next_period])==0:
                return True
            return False
        else:
            if len([(course_id2,lecture_id2) for course_id2 in self.problem.curriculas[course_curricula] for lecture_id2 in range(self.problem.courses[course_id2]) if self.course_solution[(course_id2,lecture_id2)][0]==next_period])==0 and len([(course_id2,lecture_id2) for course_id2 in self.problem.curriculas[course_curricula] for lecture_id2 in range(self.problem.courses[course_id2]) if self.course_solution[(course_id2,lecture_id2)][0]==previous_period])==0:
                return True
            return False

    def compute_cost(self,course_id,lecture_id):
        cost=0
        # 1. isolated lectures
        cost+=len([(course_id,lecture_id) for course_id,lecture_id in self.lectures if self.is_isolated_lecture(course_id)])

        # 2. Time windows
        for curricula_id in range(self.problem.num_curriculas):
            for day in range(self.problem.days):
                curricula_day_periods=[self.course_solution[(course_id,lecture_id)][0] for course_id in self.problem.curriculas[curricula_id] for lecture_id in range(self.problem.courses[course_id].lectures) if self.course_solution[(course_id,lecture_id)][0] in list(range(day*self.problem.periods_per_day,day*self.problem.periods_per_day+self.problem.periods_per_day))]
                min_day_period=min(curricula_day_periods)
                max_day_period=max(curricula_day_periods)
                for period_id in range(day*self.problem.periods_per_day,day*self.problem.periods_per_day+self.problem.periods_per_day):
                    if period_id<min_day_period or period_id>max_day_period:
                        continue
                    elif period_id in curricula_day_periods:
                        continue
                    else:
                        cost+=1

        # 3. Room stability
        for course_id in range(self.problem.num_courses):
            cost+=len({self.course_solution[(course_id,lecture_id)][1] for lecture_id in range(self.problem.courses[course_id])})-1
        
        # 4. Student Min Max load
        for curricula_id in range(self.problem.num_curriculas):
            for day in range(self.problem.days):
                curricula_day_courses=len([(course_id,lecture_id) for course_id in self.problem.curriculas[curricula_id] for lecture_id in range(self.problem.courses[course_id].lectures) if self.course_solution[(course_id,lecture_id)][0] in list(range(day*self.problem.periods_per_day,day*self.problem.periods_per_day+self.problem.periods_per_day))])
                if curricula_day_courses<self.problem.min_daily_courses:
                    cost+=abs(curricula_day_courses-self.problem.min_daily_courses) 
                elif curricula_day_courses>self.problem.max_daily_lectures:
                    cost+=curricula_day_courses-self.problem.max_daily_lectures

        # 5. Travel Distance
        for curricula_id in range(self.problem.num_curriculas):
            for day in range(self.problem.days):
                for period_id in range(day*self.problem.periods_per_day,day*self.problem.periods_per_day+self.problem.periods_per_day-1):
                    course_id_period=[(course_id,lecture_id) for course_id in range(self.problem.num_courses) for lecture_id in range(self.problem.courses[course_id].lectures) if self.course_solution[(course_id,lecture_id)][0]>period_id]
                    course_id_period_next=[(course_id,lecture_id) for course_id in range(self.problem.num_courses) for lecture_id in range(self.problem.courses[course_id].lectures) if self.course_solution[(course_id,lecture_id)][0]>period_id+1]
                    if len(course_id_period)==0 or len(course_id_period_next)==0: continue
                    course_id_period,lecture_id_period=course_id_period[0]
                    course_id_period_next,lecture_id_period_next=course_id_period_next[0]
                    cost+=abs(self.problem.rooms[self.course_solution[(course_id_period,lecture_id_period)][1]].id-self.problem.rooms[self.course_solution[(course_id_period_next,lecture_id_period_next)][1]].id)  

        # 6. Double lectures
        for course_id in range(self.problem.num_courses):
            for lecture_id in range(self.problem.courses[course_id].lectures):
                period_id=self.course_solution[(course_id,lecture_id)][0]
                next_period_course=[(course_id,lecture_id2) for lecture_id2 in self.problem.courses[course_id].lectures if self.course_solution[(course_id,lecture_id2)]==period_id+1 and lecture_id2!=lecture_id]
                previous_period_course=[(course_id,lecture_id2) for lecture_id2 in self.problem.courses[course_id].lectures if self.course_solution[(course_id,lecture_id2)]==period_id-1 and lecture_id2!=lecture_id]
                if len(next_period_course)==0 and len(previous_period_course)==0:
                    cost+=1
        return cost
    
    def read(self):
        with open(os.path.join(Solution.path_to_solution,f'{self.id}.sol'),'r') as RF:
            for line in RF:
                course_id,lecture_id,period_id,room_id=line.strip().split()
                self.course_solution[(course_id,lecture_id)]=(period_id,self.problem.room_numeric_id[room_id])
        
    def save(self):
        with open(os.path.join(Solution.path_to_solution,f'{self.id}_{self.compute_cost()}.sol'),'w') as WF:
            for (course_id,lecture_id),(period_id,room_id) in self.course_solution.items():
                WF.write(f'{course_id} {lecture_id} {period_id} {self.rooms[room_id].id}\n')