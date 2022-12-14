import os
from problem import Problem
from ortools.sat.python import cp_model
from itertools import combinations


def initial_solution(problem:Problem,timesol):
    model=cp_model.CpModel()
    xvars={(event_id,room_id,period_id):model.NewBoolVar(name=f'{event_id}_{room_id}_{period_id}') for event_id in problem.number_of_events() for room_id in range(problem.number_of_rooms()) for period_id in range(problem.number_of_periods())}

    for event_id in range(problem.number_of_events()):
        model.Add(
            sum([xvars[(event_id,room_id,period_id)] for room_id in range(problem.number_of_rooms()) for period_id in range(problem.number_of_periods())])==1
        )
    
    # 1. Consecutive theory lectures
    # A consecutive lecture consists of two lectures and practilly generate a lecture consists of two periods
    # e.g course1-->hours:4
    # lectureA=lecture1+lecture2
    # lectureB=lecture3+lecture4

    for consecutive in problem.consecutive_theories:
        for room_id in range(problem):
            for period_id in range(problem.number_of_periods()-1):
                model.Add(
                    sum([
                        xvars[(course,lecture_id1,room_id,period_id)]
                        for room_id in range(problem.number_of_rooms())
                    ])==
                    sum([
                        xvars[((course,lecture_id2,room_id,period_id+1))]
                        for room_id in range(problem.number_of_rooms())
                    ])
                )
    # 2. Consecutive laboratary
    for course,consecutive in problem.consecutive_labs.items():
        for lecture_id1,lecture_id2 in consecutive:
            for room_id in range(problem.number_of_rooms()):
                for period_id in range(problem.number_of_periods()-1):
                    model.Add(
                        xvars[(course,lecture_id1,room_id,period_id)]==xvars[(course,lecture_id2,room_id,period_id)]
                    )
    
    # 3. Neighbor courses should not be placed in the same period
    for event_id in range(problem.number_of_events()):
        for neighbor_event_id in problem.G.neighbors(event_id):
            for period_id in range(problem.number_of_periods()):
                model.Add(
                    sum([
                        xvars[(event_id,room_id,period_id)]
                        for room_id in range(problem.number_of_rooms())
                    ])
                    +sum([
                        xvars[(neighbor_event_id,room_id,period_id)]
                        for room_id in range(problem.number_of_rooms())
                    ])
                    <=1
                )
    
    # 4. Events of the same lecturer should not be placed in the same period. 
    for _,lecturer_events in problem.lecturer_events:
        for event_id1,event_id2 in combinations(lecturer_events,2):
            for period_id in range(problem.number_of_periods()):
                model.Add(
                    sum([
                        xvars[(event_id1,room_id,period_id)]
                        for room_id in range(problem.number_of_rooms())
                    ])+
                    sum([
                        xvars[(event_id2,room_id,period_id)]
                        for room_id in range(problem.number_of_rooms())
                    ])
                    <=1
                )

    for event_id1,event_id2 in problem.G.edges:
        for period in range(problem.number_of_periods()):
            consecutive_relation=model.NewBoolVar(name=f'consecutive_relation_{event_id1}_{event_id2}_{period}')
            model.Add(

            )

    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=timesol
    solver.parameters.num_search_workers=os.cpu_count()
    status=solver.Solve(model=model)
    esol={}
    if status in [cp_model.OPTIMAL,cp_model.FEASIBLE]:
        for (event_id,room_id,period_id),dvar in xvars.items():
            if solver.Value(dvar)==1:
                esol[event_id]=(room_id,period_id)
    return esol
