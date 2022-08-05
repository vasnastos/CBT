from ortools.sat.python import cp_model
import os
from collections import defaultdict
from tqdm import tqdm
from functools import reduce
import networkx as nx


signs=['COURSES:','ROOMS:','CURRICULA:','UNAVAILABILITY_CONSTRAINTS:','ROOM_CONSTRAINTS:']

# self.course_rooms =>Valid rooms per course
# self.course_periods=>Valid periods per course
# self.G=>Conflicting course(teacher,room,curricula)
# self.R=>Number of rooms
# self.C=>Number of courses
# self.L=>Number of lectures
# self.P=>Number of periods
# self.LC=>Number of lecturers


class CTT:
    _path_to_datasets=os.path.join('','datasets','udine_datasets')
    _udine_datasets=os.listdir(os.path.join('','datasets','udine_datasets'))
    _dit_datasets=os.listdir(os.path.join('','datasets','dit_fall')) # To be  done

    def __init__(self,ds_name):
        cfp={}
        content=''
        self.courses={}
        self.rooms={}
        self.curricula={}
        self.lecturers=set()
        self.lectures=list()
        self.course_curricula=dict()
        self.id=ds_name
        
        with open(os.path.join(CTT._path_to_datasets,self.id),'r') as RF:
            for _ in range(9):
                line=RF.readline()
                data=line.split(':')
                cfp[data[0].strip()]=data[1].strip()

            for line in RF:
                if len(line.strip())==0: continue
                if line.strip()=="END.": break
                if line.strip() in signs:
                    content=line.strip().replace(':','')
                    continue
            
                data=line.split()

                if content=='COURSES':
                    cid=data[0].strip()
                    self.courses[cid]=dict()
                    self.courses[cid]['t']=data[1].strip()
                    self.lecturers.add(data[1].strip())
                    self.courses[cid]['l']=int(data[2].strip())
                    self.courses[cid]['d']=int(data[3].strip())
                    self.courses[cid]['s']=int(data[4].strip())
                    self.courses[cid]['bid']=int(data[5].strip())
                    self.courses[cid]['UC']=list()
                    self.courses[cid]['RC']=list()
                    for i in range(int(data[2].strip())):
                        self.lectures.append((cid,i))
                
                elif content=='ROOMS':
                    self.rooms[data[0].strip()]=dict()
                    self.rooms[data[0].strip()]['C']=int(data[1].strip())
                    self.rooms[data[0].strip()]['bid']=int(data[2].strip())
                
                elif content=='CURRICULA':
                    cid=data[0].strip()
                    self.curricula[cid]=list()
                    for i in range(2,len(data)):
                        self.curricula[cid].append(data[i].strip())
                        self.course_curricula[data[i].strip()]=cid
                    
                elif content=='UNAVAILABILITY_CONSTRAINTS':
                    cid=data[0].strip()
                    self.courses[cid]['UC'].append((int(data[1].strip()),int(data[2].strip())))
                
                elif content=='ROOM_CONSTRAINTS':
                    cid=data[0].strip()
                    self.courses[cid]['RC'].append(data[1].strip())

        self.R=len(self.rooms)
        self.C=len(self.courses)
        self.L=len(self.lectures)
        self.LC=len(self.lecturers)
        self.days=int(cfp['Days'])
        self.ppd=int(cfp['Periods_per_day'])
        self.P=self.days*self.ppd
        self.min_daily_lectures,self.max_daily_lectures=[int(i) for i in cfp['Min_Max_Daily_Lectures'].strip().split()]

        self.course_rooms=defaultdict(list)
        self.course_periods=defaultdict(list)
        self.lecturer_courses=defaultdict(list)
        self.one_room_courses=list()
        self.scheduled_sols=dict()
        self.last_day_periods=[d*self.ppd+self.ppd-1 for d in range(self.days)]
        self.first_day_periods=[d*self.ppd for d in range(self.days)]

        for course_id,cfp in self.courses.items():
            if self.R-len(cfp['RC'])==1:
                self.one_room_courses.append(course_id)
            self.lecturer_courses[cfp['t']].append(course_id)
            for rid in list(self.rooms.keys()):
                if rid not in cfp['RC']:
                    self.course_rooms[course_id].append(rid)
            for d in range(self.days):
                for p in range(self.ppd):
                    if (d,p) not in cfp['UC']:
                        self.course_periods[course_id].append(d*self.ppd+p)

        # Construct graph to translate the problem
        self.nx_graph()

    def nx_graph(self):
        self.G=nx.Graph()
        self.G.add_nodes_from([cid for cid in list(self.courses.keys())])
        for _,course_list in self.curricula.items():
            for cid in course_list:
                for cid2 in course_list:
                    if cid==cid2: continue
                    self.G.add_edge(cid,cid2)
        
        for _,lecturerc in self.lecturer_courses.items():
            for cid in lecturerc:
                for cid2 in lecturerc:
                    if cid==cid2: continue
                    self.G.add_edge(cid,cid2)
        
        for course_id in self.one_room_courses:
            for course_id2 in self.one_room_courses:
                if course_id==course_id2: continue
                self.G.add_edge(course_id,course_id2)
    
    def set_solution(self,esol):
        self.scheduled_sols=esol
    
    def save(self):
        with open(os.path.join('','solutions',f'{self.id.replace("ectt","")}.sol'),'w') as WF:
            for (cid,aid),(rid,pid) in self.scheduled_sols.items():
                WF.write(f'{cid} {aid} {rid} {pid}\n')
        
    def __str__(self) -> str:
        msg='Schedule'
        for (cid,aid),(rid,pid) in self.scheduled_sols.items():
            msg+=f'Lecture_{cid}_{aid}=>({rid},{pid})\n'
        return msg

def udine_solver1(problem:CTT,objectivef=True,timesol=600):
    model=cp_model.CpModel()
    lvars={(cid,aid,rid,p):model.NewBoolVar(name=f'{cid}_{aid}_{rid}_{p}') for cid in list(problem.courses.keys()) for aid in range(problem.courses[cid]['l']) for rid in problem.course_rooms[cid] for p in problem.course_periods[cid]}
    
    # 1.All courses must be scheduled
    for (cid,aid) in problem.lectures:
        model.Add(sum([lvars[(cid,aid,rid,pid)] for rid in problem.course_rooms[cid] for pid in problem.course_periods[cid]])==1)

    # 2. Periods must have leq courses in a period based on the number of the rooms
    for pid in range(problem.P):
        model.Add(sum([lvars[(cid,aid,rid,pid)] for (cid,aid) in problem.lectures for rid in problem.course_rooms[cid] if pid in problem.course_periods[cid]])<=problem.R)
     
    # 3. Lectures of the same course should not be assigned in the same period
    for cid,cfp in problem.courses.items():
        for i in range(cfp['l']):
            for j in range(i+1,cfp['l']):
                model.Add(sum([lvars[(cid,i,rid,pid)]*pid for rid in problem.course_rooms[cid] for pid in problem.course_periods[cid]])!=sum([lvars[(cid,j,rid,pid)]*pid for rid in problem.course_rooms[cid] for pid in problem.course_periods[cid]]))

    # 4.Neighbor lectures(lectures of two conflict courses) should not be assigned in the same period
    for (cid,aid) in problem.lectures:
        for cid2 in problem.G.neighbors(cid):
            for pid in range(problem.P):
                if pid not in problem.course_periods[cid] or pid not in problem.course_periods[cid2]: continue
                model.Add(sum([lvars[(cid,aid,rid,pid)] for rid in problem.course_rooms[cid]])+sum([lvars[(cid2,aid2,rid,pid)] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.course_rooms[cid2]])<=1)
    
    if objectivef:
        # extra decision variables 
        daily_lessons=[x for x in range(problem.days) if x!=problem.min_daily_lectures and x!=problem.max_daily_lectures]
        working_days={(cid,i):model.NewBoolVar(name=f'working_days_{cid}') for cid in list(problem.courses.keys()) for i in range(1,problem.courses[cid]['d'])}
        isolated_lectures={(cid,aid):model.NewBoolVar(name=f'isolated_lecture_{cid}_{aid}') for cid,aid in problem.lectures}
        time_windows={(curr_id,p):model.NewBoolVar(name=f'no_teaching_period_{p}_curr_{curr_id}') for curr_id in list(problem.curricula.keys()) for p in range(problem.P)}
        daily_lectures_load={(curr_id,d,i):model.NewBoolVar(name=f'students_load_{curr_id}_{i}') for curr_id in list(problem.curricula.keys()) for d in range(problem.days) for i in daily_lessons}
        travel_distance={(cid,aid):model.NewBoolVar(name=f'travel_distance_{cid}_{aid}') for (cid,aid) in problem.lectures}


        # Working days cost component(MinWorkingDays)
        for cid in list(problem.courses.keys()):
            for i in range(1,problem.courses[cid]['d']):
                model.Add(
                    -len({lvars[(cid,aid,rid,pid)]*(pid//problem.ppd) for aid in range(problem.courses[cid]['l']) for rid in problem.course_rooms[cid] for pid in problem.course_periods[cid]})
                    +working_days[(cid,i)]
                    >=-(i-1)
                )

        # # Isolated lectures cost component(IsolatedLectures)
        # for cid,aid in problem.lectures:
        #     for d in range(problem.days):
        #         for p in range(d*problem.ppd,d*problem.ppd+problem.ppd):
        #             previous_period=p-1
        #             next_period=p+1
        #             extern_lectures=[i for i in range(problem.courses[cid]['l']) if i!=aid]
        #             if previous_period<d*problem.ppd:
        #                 model.Add(
        #                     sum([lvars[(cid2,aid2,rid,next_period)] for cid2 in problem.G.neighbors(cid) for aid2 in range(problem.courses[cid2]['d']) for rid in problem.course_rooms[cid2] if next_period in problem.course_periods[cid2]])
        #                     +sum([lvars[(cid,aid2,rid,next_period)] for aid2 in extern_lectures for rid in problem.course_rooms[cid] if next_period in problem.course_periods[cid]])
        #                     -sum([lvars[(cid,aid,rid,p)] for rid in problem.course_rooms[cid] if p in problem.course_periods[cid]])
        #                     +isolated_lectures[(cid,aid)]
        #                     >=0
        #                 ) 
        #             elif next_period==d*problem.ppd+problem.ppd:
        #                 model.Add(
        #                     sum([lvars[(cid2,aid2,rid,previous_period)] for cid2 in problem.G.neighbors(cid) for aid2 in range(problem.courses[cid2]['d']) for rid in problem.course_rooms[cid2] if previous_period in problem.course_periods[cid2]])
        #                     +sum([lvars[(cid,aid2,rid,previous_period)] for aid2 in extern_lectures for rid in problem.course_rooms[cid] if previous_period in problem.course_periods[cid]])
        #                     -sum([lvars[(cid,aid,rid,p)] for rid in problem.course_rooms[cid] if p in problem.course_periods[cid]])
        #                     +isolated_lectures[(cid,aid)]>=0
        #                 )
        #             else:
        #                 model.Add(
        #                     sum([lvars[(cid2,aid2,rid,previous_period)] for cid2 in problem.G.neighbors(cid) for aid2 in range(problem.courses[cid2]['d']) for rid in problem.course_rooms[cid2] if previous_period in problem.course_periods[cid2]])
        #                     +sum([lvars[(cid,aid2,rid,previous_period)] for aid2 in extern_lectures for rid in problem.course_rooms[cid] if previous_period in problem.course_periods[cid]])
        #                     -sum([lvars[(cid,aid,rid,p)] for rid in problem.course_rooms[cid] if p in problem.course_periods[cid]])
        #                     +sum([lvars[(cid2,aid2,rid,next_period)] for cid2 in problem.G.neighbors(cid) for aid2 in range(problem.courses[cid2]['d']) for rid in problem.course_rooms[cid2] if next_period in problem.course_periods[cid2]])
        #                     +sum([lvars[(cid,aid2,rid,next_period)] for aid2 in extern_lectures for rid in problem.course_rooms[cid] if next_period in problem.course_periods[cid]])
        #                     +isolated_lectures[(cid,aid)]
        #                     >=0
        #                 )

        # # Time windows between lectures in each curricula(Windows)
        # for curricula_id in list(problem.curricula.keys()):
        #     for d in range(problem.days):
        #         for pid in range(d*problem.ppd,d*problem.ppd+problem.ppd):
        #             if pid==d*problem.ppd or pid==problem.ppd*d+problem.ppd-1: continue
        #             y1decision=model.NewBoolVar(name=f'y1_{curricula_id}_{d}_{pid}')
        #             y2decision=model.NewBoolVar(name=f'y2_{curricula_id}_{d}_{pid}_')
        #             y3decision=model.NewBoolVar(name=f'final_decision_{curricula_id}_{d}_{pid}_')
                    
        #             model.Add(
        #                 sum([lvars[(cid,aid,rid,p)] for cid in problem.curricula[curricula_id] for aid in range(problem.courses[cid]['l']) for rid in problem.course_rooms[cid] for p in range(pid-1,d*problem.ppd,-1) if p in problem.course_periods[cid]])
        #                 +y1decision>=1
        #             )

        #             model.Add(
        #                 sum([lvars[(cid,aid,rid,p)] for cid in problem.curricula[curricula_id] for aid in range(problem.courses[cid]['l']) for rid in problem.course_rooms[cid] for p in range(pid+1,d*problem.ppd+problem.ppd) if p in problem.course_periods[cid]])
        #                 +y2decision>=1
        #             )

        #             model.Add(
        #                 y1decision+y2decision+y3decision>=1
        #             )

        #             model.Add(
        #                 sum([lvars[(cid,aid,rid,pid)] for cid in problem.curricula[curricula_id] for aid in range(problem.courses[cid]['l']) for rid in problem.course_rooms[cid] if pid in problem.course_periods[cid]])
        #                 +time_windows[(curricula_id,pid)]>=1
        #             ).OnlyEnforceIf(y3decision)

        #             model.Add(
        #                 time_windows[(curricula_id,pid)]==0
        #             ).OnlyEnforceIf(y3decision.Not())

        # # StudentMinMaxLoad
        # for curricula_id in list(problem.curricula.keys()):
        #     for d in range(problem.days):
        #         for i in daily_lessons:
        #             model.Add(
        #                 -sum([lvars[(cid,aid,rid,pid)] for cid in problem.curricula[curricula_id] for aid in range(problem.courses[cid]['l']) for rid in problem.course_rooms[cid] for pid in range(d*problem.ppd,d*problem.ppd+problem.ppd) if pid in problem.course_periods[cid]])
        #                 +daily_lectures_load[(curricula_id,d,i)]>=-(i-1)
        #             )

        # for (cid,aid) in problem.lectures:
        #     for pid in problem.course_periods[cid]:
        #         if pid in problem.last_day_periods : continue
        #         model.Add(
        #             sum([lvars[(cid,aid,rid,pid)] * problem.rooms[rid]['bid'] for rid in problem.course_rooms[cid]])
        #             +sum([lvars[(cid2,aid2,rid,pid+1)] * problem.rooms[rid]['bid'] for cid2 in [x for x in problem.curricula[problem.course_curricula[cid]] if x!=cid] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.course_rooms[cid2] if pid+1 in problem.course_periods[cid2]])
        #             +travel_distance[(cid,aid)]>=2
        #         )

        # Objective value
        objective=[
            sum([working_days[(cid,i)]*abs(i-problem.courses[cid]['d']) for cid in list(problem.courses.keys()) for i in range(1,problem.courses[cid]['d'])]) # Min working days soft violation
            # ,sum([isolated_lectures[(cid,aid)] for cid,aid in problem.lectures])
            # ,sum([time_windows[(curricula_id,p)] for curricula_id in list(problem.curricula.keys()) for p in range(problem.P)])
            # ,sum([daily_lectures_load[(curricula_id,d,i)] * (abs(i-problem.min_daily_lectures) if i<problem.min_daily_lectures else i-problem.max_daily_lectures) for curricula_id in list(problem.curricula.keys()) for d in range(problem.days) for i in daily_lessons])
            # ,sum([travel_distance[(cid,aid)] for (cid,aid) in problem.lectures])
        ]

        model.Minimize(sum(objective))

    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=timesol
    solver.parameters.num_search_workers=os.cpu_count()
    status=solver.Solve(model,cp_model.ObjectiveSolutionPrinter())
    esol={}
    print(solver.StatusName(status))
    if status==cp_model.OPTIMAL or status==cp_model.FEASIBLE:
        for (cid,aid,rid,pid),dvar in lvars.items():
            if solver.Value(dvar)==1:
                esol[(cid,aid)]=(rid,pid)
    return esol

def udine_solver2(problem):
    model=cp_model.CpModel()
    lvars={(cid,aid,rid,pid):model.NewBoolVar(name=f'dvar_{cid}_{aid}_{rid}_{pid}') for cid in list(problem.courses.keys()) for aid in range(problem.courses[cid]['l']) for rid in list(problem.rooms.keys()) for pid in problem.course_periods[cid]}

    for (cid,aid) in problem.lectures:
        model.Add(sum([lvars[(cid,aid,rid,pid)] for rid in list(problem.rooms.keys()) for pid in problem.course_periods[cid]])==1)
    
    for pid in range(problem.P):
        model.Add(sum([lvars[(cid,aid,rid,pid)] for (cid,aid) in problem.lectures for rid in list(problem.rooms.keys()) if pid in problem.course_periods[cid]])<=problem.R)
    
    # Lectures of course must not be on the same period--In dit-ctt change that and look at the lecturers schedule  
    # because two lectures of a course can be executed on the same period by a different lecturer!!! 
    for cid in list(problem.courses.keys()):
        for pid in problem.course_periods[cid]:
            model.Add(sum([lvars[(cid,aid,rid,pid)] for aid in range(problem.courses[cid]['l']) for rid in list(problem.rooms.keys())])<=1)


    for (cid,aid) in problem.lectures:
        for cid2 in list(problem.G.neighbors(cid)):
            for pid in range(problem.P):
                if pid not in problem.course_periods[cid] or pid not in problem.course_periods[cid2]: continue
                model.Add(sum([lvars[(cid,aid,rid,pid)] for rid in list(problem.rooms.keys())])+sum([lvars[(cid2,aid2,rid,pid)] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.rooms.keys()])<=1)

    working_days={(cid,i):model.NewBoolVar(name=f'working_days_{cid}_{i}') for cid in list(problem.courses.keys()) for i in range(1,problem.courses[cid]['d'])}
    isolated_lectures={(cid,aid):model.NewBoolVar(name=f'isolated_lecture_{cid}_{aid}') for (cid,aid) in problem.lectures}
    time_windows={(curr_id,pid):model.NewBoolVar(name=f'time_windows_{curr_id}_{pid}') for curr_id in list(problem.curricula.keys()) for pid in range(problem.P) if pid not in problem.first_day_periods and pid not in problem.last_day_periods}
    room_stability={(cid,aid):model.NewBoolVar(name=f'room_stability_{cid}_{aid}') for cid in list(problem.courses.keys()) for aid in range(problem.courses[cid]['l'])}

    for cid in list(problem.courses.keys()):
        for i in range(1,problem.courses[cid]['d']):
            model.Add(
                -len({lvars[(cid,aid,rid,pid)] * (pid//problem.ppd) for aid in range(problem.courses[cid]['l']) for rid in problem.rooms.keys() for pid in problem.course_periods[cid]})
                +working_days[(cid,i)]<=-(i-1)                
            )
    
    for (cid,aid) in problem.lectures:
        for pid in problem.course_periods[cid]:
            previous_period=pid-1
            next_period=pid+1
            if pid in problem.last_day_periods:
                model.Add(
                    sum([lvars[(cid2,aid2,rid,previous_period)] for cid2 in problem.curricula[problem.course_curricula[cid]] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.course_rooms[cid2] if previous_period in problem.course_periods[cid2]])
                    +isolated_lectures[(cid,aid)]>=1
                )
            elif pid in problem.first_day_periods:
                model.Add(
                    sum([lvars[(cid2,aid2,rid,next_period)] for cid2 in problem.curricula[problem.course_curricula[cid]] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.course_rooms[cid2] if next_period in problem.course_periods[cid2]])
                    +isolated_lectures[(cid,aid)]>=1
                )
            else:
                model.Add(
                    sum([lvars[(cid2,aid2,rid,previous_period)] for cid2 in problem.curricula[problem.course_curricula[cid]] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.course_rooms[cid2] if previous_period in problem.course_periods[cid2]])
                    +sum([lvars[(cid2,aid2,rid,next_period)] for cid2 in problem.curricula[problem.course_curricula[cid]] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.course_rooms[cid2] if next_period in problem.course_periods[cid2]])
                    +isolated_lectures[(cid,aid)]>=1
                ) 
    
    for curricula_id in list(problem.curricula.keys()):
        for d in range(problem.days):
            for pid in range(d*problem.ppd+1,d*problem.ppd+problem.ppd-1):
                y1decision=model.NewBoolVar(name=f'time_windows_y1_{curricula_id}_{d}_{pid}')
                y2decision=model.NewBoolVar(name=f'time_windows_y2_{curricula_id}_{d}_{pid}')
                y3decision=model.NewBoolVar(name=f'time_windows_y3_{curricula_id}_{d}-{pid}')
                
                model.Add(
                    sum([lvars[(cid,aid,rid,p)] for cid in problem.curricula[problem.course_curricula[cid]] for aid in range(problem.courses[cid]['l']) for rid in list(problem.rooms.keys()) for p in range(pid-1,d*problem.ppd,-1) if p in problem.course_periods[cid]])
                    +y1decision>=1
                )

                model.Add(
                    sum([lvars[(cid,aid,rid,p)] for cid in problem.curricula[problem.course_curricula[cid]] for aid in range(problem.courses[cid]['l']) for rid in list(problem.rooms.keys()) for p in range(pid+1,d*problem.ppd+problem.ppd) if p in problem.course_periods[cid]])
                    +y2decision>=1
                )

                model.Add(
                    y1decision
                    +y2decision
                    +y3decision>=1
                )

                model.Add(
                    sum([lvars[(cid,aid,rid,pid)] for cid in problem.curricula[problem.course_curricula[cid]] for aid in range(problem.courses[cid]['l']) for rid in list(problem.rooms.keys()) if pid in problem.course_periods[cid]])
                    +time_windows[(curricula_id,pid)]>=1
                ).OnlyEnforceIf(y3decision)


    for (cid,aid) in problem.lectures:
        for pid in problem.course_periods[cid]:
            model.Add(
                sum([lvars[(cid,aid,rid,pid)]*problem.rooms[rid]['bid'] for rid in problem.course_rooms[cid]])
                +sum([lvars[(cid2,aid2,rid,pid+1)]*problem.rooms[rid]['bid'] for cid2 in problem.curricula[problem.course_curricula[cid]] for aid2 in range(problem.courses[cid2]['l']) for rid in problem.course_rooms[cid2] if pid+1 in problem.course_periods[cid2]])
                +room_stability[(cid,aid)]>=2
            )


    objective=[
        sum([working_days[(cid,i)]*(problem.courses[cid]['d']-i) for cid in list(problem.courses.keys()) for i in range(1,problem.courses[cid]['d'])])
        ,sum([isolated_lectures[(cid,aid)] for (cid,aid) in problem.lectures])
        ,sum([time_windows[(curricula_id,pid)] for curricula_id in list(problem.curricula.keys()) for pid in range(problem.P) if pid not in problem.first_day_periods and pid not in problem.last_day_periods])
        ,sum([room_stability[(cid,aid)] for (cid,aid) in problem.lectures])
    ]

    model.Minimize(sum(objective))

    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=10
    solver.parameters.num_search_workers=os.cpu_count()
    status=solver.Solve(model,cp_model.ObjectiveSolutionPrinter())
    print(solver.StatusName(status))
    if status==cp_model.FEASIBLE or status==cp_model.OPTIMAL:
        for (cid,aid,rid,pid),dv in lvars.items():
            if solver.Value(dv):
                print(f'c_{cid}_{aid}=>({rid},{pid})')
    

def udine_solver3():
    pass


def scenario1():
    problem=CTT("toy.ectt")
    esol=udine_solver1(problem=problem,objectivef=True)
    print(esol)
    # problem.set_solution(esol)
    # problem.save()

def scenario2():
    problem=CTT("toy.ectt")
    udine_solver2(problem=problem)
    # problem.set_solution(esol)
    # problem.save()

if __name__=='__main__':
    # scenario1()
    scenario2()