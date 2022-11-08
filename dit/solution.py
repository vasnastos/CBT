from dit.problem import Problem
from tabulate import tabulate
from itertools import bidict
import os,logging,random,math,pandas as pd
from time import time

class Solution:
    path_to_solution=os.path.join('','solutions')
    path_to_generic_solution=os.path.join('','solutions','dit_winter','dit_solution.txt')

    period_id_twist=bidict({
        "08:00-09:00":1,
        "09:00-10:00":2,
        "10:00-11:00":3,
        "11:00-12:00":4,
        "12:00-13:00":5,
        "13:00-14:00":6,
        "14:00-15:00":7,
        "15:00-16:00":8,
        "16:00-17:00":9,
        "17:00-18:00":10,
        "18:00-19:00":11,
        "19:00-20:00":12
    })

    def __init__(self,ds_name):        
        self.problem=Problem()
        self.problem.read_instance(ds_name)
        self.lectures_solution={}
        self.periodwise_solution={}
        self.roomwise_solution={}

    def read(self,solution_file_name:str):
        with open(os.path.join(Solution.path_to_solution,solution_file_name),'r') as RF:
            for line in RF:
                data=line.split()
                self.lectures_solution[(data[0].strip(),data[1].strip())]=(data[2].strip(),data[3].strip())
                self.periodwise_solution[int(data[2].strip())]=(data[1].strip(),data[2].strip())

    def save(self):
        with open(Solution.path_to_generic_solution,'r') as WF:
            for (course_id,lecture_id),(period_id,room_id) in self.lectures_solution.items():
                WF.write(f'{course_id} {lecture_id} {period_id} {room_id}\n')

    def to_excel(self):        
        for semester_id in range(1,self.problem.semester+1):
            rows=[["" for _ in self.problem.days] for _ in range(self.problem.days)]
            for (course_id,_),(period_id,room_id) in self.lectures_solution.items():
                if course_id not in self.problem.curriculas[semester_id]: continue
                rows[period_id%self.problem.periods_per_day][period_id//self.problem.periods_per_day]=f"{self.problem.courses[self.courses.find(course_id)].name}\n{self.problem.rooms[room_id].id}"

            pd.DataFrame(rows,columns=[" ","ΔΕΥΤΕΡΑ","ΤΡΙΤΗ","ΤΕΤΑΡΤΗ","ΠΕΜΠΤΗ","ΠΑΡΑΣΚΕΥΗ"],index=list(Solution.period_id_twist.keys())).to_excel(os.path.join(Solution.path_to_solution,f'dit_semester_{semester_id}.xlsx'))
    
    def schedule(self,course_id,lecture_id,room_id,period_id):
        self.lectures_solution[(course_id,lecture_id)]=(period_id,room_id)
        self.roomwise_solution[room_id].append((course_id,lecture_id))
        self.periodwise_solution[period_id].append((course_id,lecture_id))
    
    def unschedule(self,course_id,lecture_id):
        self.roomwise_solution[self.lectures_solution[(course_id,lecture_id)][1]].remove((course_id,lecture_id))
        self.periodwise_solution[self.lectures_solution[(course_id,lecture_id)][0]].remove((course_id,lecture_id))
        self.lectures_solution[(course_id,lecture_id)]=(-1,-1)
    
    def semester_scheduling(self,semester_id)->str:
        periods_table={
            "08:00-09:00":["","","","","",""],
            "09:00-10:00":["","","","","",""],
            "10:00-11:00":["","","","","",""],
            "11:00-12:00":["","","","","",""],
            "12:00-13:00":["","","","","",""],
            "13:00-14:00":["","","","","",""],
            "14:00-15:00":["","","","","",""],
            "15:00-16:00":["","","","","",""],
            "16:00-17:00":["","","","","",""],
            "17:00-18:00":["","","","","",""],
            "18:00-19:00":["","","","","",""],
            "19:00-20:00":["","","","","",""]
        }
        for (course_id,lecture_id),(period_id,room_id) in self.lectures_solution.items():
            if self.courses[course_id].semester==semester_id:
                record_id=period_id%self.problem.periods_per_day
                day=period_id//self.problem.periods_per_day
                if periods_table[record_id][day]=="":
                    periods_table[record_id][day]=f'{course_id}_{"Εργαστήριο" if lecture_id>self.courses[course_id].theory_hours+self.courses[course_id].tutoring_hours else "ΦΡΟΝΤΗΣΤΗΡΙΟ" if lecture_id>self.courses[course_id].theory_hours else ""}\n{self.problem.rooms[room_id]}'
                else:
                    periods_table[record_id][day]=f', {course_id}_{"Εργαστήριο" if lecture_id>self.courses[course_id].theory_hours+self.courses[course_id].tutoring_hours else "ΦΡΟΝΤΗΣΤΗΡΙΟ" if lecture_id>self.courses[course_id].theory_hours else ""}\n{self.problem.rooms[room_id]}'
        print(f'Semester {semester_id}')
        print('-'*20)
        return str(tabulate(
            [[hour_name]+courses_in_period for hour_name,courses_in_period in self.periods_table.items()],headers=['   ','ΔΕΥΤΕΡΑ','ΤΡΙΤΗ','ΤΕΤΑΡΤΗ','ΠΕΜΠΤΗ','ΠΑΡΑΣΚΕΥΗ'],tablefmt='fancygrid'
        ))+"\n\n"
    
    def validate_solution(self):
        logger=logging.getLogger("Dit_solver_logger")
        logger.setLevel(logging.INFO)
        formatter=logging.Formatter("%(asctime)s\t%(message)s")
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)


        for (course_id,lecture_id),(period_id,room_id) in self.lectures_solution.items():
            for course_id_conflicted in self.problem.semester_courses[self.courses[course_id].semester]:
                if course_id==course_id_conflicted: continue
                violations=[(course_id_conflicted,lecture_id_conflicted) for lecture_id_conflicted in range(self.problem.courses[course_id_conflicted].number_of_lectures) if self.lectures_solution[(course_id,lecture_id)][0]==self.lectures_solution[(course_id_conflicted,lecture_id_conflicted)][0]]
                if len(violations)>0:
                    for violation in violations:
                        logger.info(f'({course_id},{lecture_id}),{violation} violated constraints in period:{self.lectures_solution[(course_id,lecture_id)][0]}')
                    total_violations+=len(violations)
        
        logger.info(f'Total hard constraint violations:{total_violations}')

    def compute_cost(self):
        pass
    
    def conflict_density(self):
        pass

    def __str__(self):
        output+=self.problem.__str__()+'\n'
        output+='\n\n'
        for i in range(1,self.problem.semesters):
            output+=self.semester_scheduling(i)
        return output