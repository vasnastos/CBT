from ortools.sat.python import cp_model
from udine.problem import Problem
import os,math,gurobipy as gpx,docplex.cp as cpx


from collections import combinations

def udine_solver_formulation(problem:Problem,time_limit=600):
    model=cp_model.CpModel()
    xvars={(course_id,lecture_id,room_id,period_id):model.NewBoolVar(name=f'formulation_{course_id}_{room_id}_{period_id}') for course_id in range(problem.num_courses) for lecture_id in range(problem.courses[course_id].lectures) for room_id in range(problem.num_rooms) for period_id in range(problem.num_periods)}

    # 1. Setup a lecture in a single room without any constraint(period-room) violated
    for course_id in range(problem.num_courses):
        for lecture_id in range(problem.courses[course_id].lectures):
            model.Add(
                sum([
                xvars[(course_id,lecture_id,room_id,period_id)]
                for room_id in range(problem.num_rooms) 
                for period_id in range(problem.num_periods)
                ])==1
            )

        for room_id in range(problem.num_rooms):
            if room_id in problem.courses[course_id].room_constraints:
                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for period_id in range(problem.num_periods)
                    ])==0
                )
            
        for period_id in range(problem.num_periods):
            if period_id in problem.courses[course_id].unavailability_constraints: 
                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                    ])==0
              )
    # 2. Lectures of a course should not be placed in the same period(differs in the problem description(etc. laboratories of a course made by 2 lecturers))
    for course_id in range(problem.num_courses):
        for lecture_id_i1 in range(problem.courses[course_id].lectures):
            for lecture_id_i2 in range(lecture_id_i1+1,problem.courses[course_id].lectures):
                for period_id in range(problem.num_periods):
                    if period_id in problem.courses[course_id].unavailability_constraints: continue
                    model.Add(
                        sum([
                            xvars[(course_id,lecture_id_i1,room_id,period_id)]
                            for room_id in range(problem.num_rooms)
                        ])
                        +
                        sum([
                            xvars[(course_id,lecture_id_i2,room_id,period_id)]
                            for room_id in range(problem.num_rooms)
                        ])
                        <=1
                    )


    # 3. At each period-room pair one lecture or no lecture should be placed
    for room_id in range(problem.num_rooms):
        for period_id in range(problem.num_periods):
            model.Add(
                sum([
                    xvars[(course_id,lecture_id,room_id,period_id)]
                    for course_id in range(problem.num_courses)
                    for lecture_id in range(problem.courses[course_id].lectures)
                ])<=1
            )    
    
    
    # 4. Lecturers of the same curricula should not be placed in the same period
    for curricula_id in range(problem.num_curriculas):
        for course_index_i in range(len(problem.curriculas[curricula_id])):
            for course_index_j in range(course_index_i+1,len(problem.curriculas[curricula_id])):
                for period_id in range(problem.num_periods):
                    if period_id in problem.courses[course_index_i].unavailability_constraints or period_id in problem.courses[course_index_j].unavailability_constraints: continue
                    model.Add(
                        sum([
                            xvars[(problem.curriculas[curricula_id][course_index_i],lecture_id,room_id,period_id)]
                            for lecture_id in range(problem.courses[course_index_i].lectures)
                            for room_id in range(problem.num_rooms)
                        ])
                        +sum([
                            xvars[(problem.curriculas[curricula_id][course_index_j],lecture_id,room_id,period_id)]
                            for lecture_id in range(problem.courses[course_index_j].lectures)
                            for room_id in range(problem.num_rooms)
                        ])<=1                        
                    )
    
    # 5. Min Working days: he lectures of each course must be spread into a given minimum number of days. Each day below the minimum counts as 1 violation
    # Will be defined directly on the objective function
    
    # --------------- SOFT CONSTRAINTS ---------------

    # 6. Isolated lectures: Lectures belonging to a curriculum should be adja-
    # cent to each other (i.e., in consecutive periods). For a given curriculum we account for a
    # violation every time there is one lecture not adjacent to any other lecture within the same
    # day. Each isolated lecture in a curriculum counts as 1 violation.
    isolated_lectures={(course_id,lecture_id):model.NewBoolVar(name=f'isolated_lecture_dv_{course_id}_{lecture_id}') for course_id in range(problem.num_courses) for lecture_id in range(problem.courses[course_id].lectures)}
    for course_id,lecture_id in problem.lectures:
        curricula_id=problem.find_curricula(course_id)
        for day in range(problem.days):
            for period in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day):
                model.Add(
                    sum([
                        xvars[(curr_course_id,curr_lecturer_id,room_id,period-1)]
                        for curr_course_id,curr_lecturer_id in problem.lectures
                        for room_id in range(problem.num_rooms)
                    ])
                    -sum([
                        xvars[(course_id,lecture_id,room_id,period)]
                        for room_id in range(problem.num_rooms)
                    ])
                    +sum([
                        xvars[(curr_course_id,curr_lecture_id,room_id,period+1)]
                        for curr_course_id,curr_lecture_id in problem.lectures
                        for room_id in range(problem.num_rooms)
                    ])
                    +isolated_lectures[(course_id,lecture_id)]>=0
                )

    # 7. Windows: Lectures belonging to a curriculum should not have time win-
    # dows (i.e., periods without teaching) between them. For a given curriculum we account for
    # a violation every time there is one windows between two lectures within the same day.
    # Each time window in a curriculum counts as many violation as its length (in periods).
    windows={(curricula_id,day,period_id):model.NewBoolVar(name=f'windows_soft_violation_{curricula_id}_{day}_{period_id}') for curricula_id in list(problem.curriculas.keys()) for day in range(problem.days) for period_id in range(day*problem.periods_per_day+1,day*problem.periods_per_day+problem.periods_per_day-1)}
    for curricula_id in list(problem.curriculas.keys()):
        for day in range(problem.days):
            for period_id in range(day*problem.periods_per_day+1,day*problem.periods_per_day+problem.periods_per_day-1):
                has_previous_course=model.NewBoolVar(name=f'previous_course_{curricula_id}_{day}_{period_id}')
                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,previous_period)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[curricula_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for previous_period in range(day*problem.periods_per_day,period_id)
                    ])>=1
                ).OnlyEnforceIf(has_previous_course)

                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,previous_period)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[curricula_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for previous_period in range(day*problem.periods_per_day,period_id)
                    ])==0
                ).OnlyEnforceIf(has_previous_course.Not())
                
                
                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id-1)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                    ])
                    +has_previous_course==1
                ).OnlyEnforceIf(windows[(curricula_id,day,period_id)])

                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id-1)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                    ])
                    +has_previous_course!=1
                ).OnlyEnforceIf(windows[(curricula_id,day,period_id)].Not())
    
    # 8. Room stability: All lectures of a course should be given in the same room. Each distinct
    # room used for the lectures of a course, but the first, counts as 1 violation.
    room_stability={(course_id,room_id):model.NewBoolVar(name=f'course_{course_id}') for course_id in range(problem.num_courses) for room_id in range(problem.num_rooms)}
    for course_id in range(problem.num_courses):
        for room_id in range(problem.num_rooms):
            model.Add(
                sum([
                    xvars[(course_id,lecture_id,room_id,period_id)]
                    for lecture_id in range(problem.num_rooms)
                    for period_id in range(day.problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                ])>=1
            ).OnlyEnforceIf(room_stability[(course_id,room_id)])

            model.Add(
                sum([
                    xvars[(course_id,lecture_id,room_id,period_id)]
                    for lecture_id in range(problem.num_rooms)
                    for period_id in range(day.problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                ])<1
            ).OnlyEnforceIf(room_stability[(course_id,room_id)].Not())

    # 9. StudentMinMaxLoad: For each curriculum the number of daily lectures should be within a
    # given range. Each lecture below the minimum or above the maximum counts as 1 violation.e
    student_min_max_load = {(curricula_id,day,load):model.NewBoolVar(name=f'students_load_{course_id}_{day}_{load}') for curricula_id in range(problem.num_curriculas) for day in range(problem.days) for load in range(0,problem.periods_per_day+1)}
    for curricula_id in list(problem.curriculas.keys()):
        for day in range(problem.days):
            for load in range(0,problem.periods_per_day+1):
                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                    ])==load
                ).OnlyEnforceIf(student_min_max_load[(curricula_id,day,load)])

                model.Add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                    ])!=load
                ).OnlyEnforceIf(student_min_max_load[(curricula_id,day,load)].Not())

    # 10. TravelDistance: Students should have the time to move from one building to another one
    # between two lectures. For a given curriculum we account for a violation every time there
    # is an instantaneous move: two lectures in rooms located in different building in two adja-
    # cent periods within the same day. Each instantaneous move in a curriculum counts as 1
    # violation.
    periods_pairs=[(period_id,period_id+1) for day in range(problem.days) for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day-1)]
    travel_distance = {(curricula_id, lb, ub):model.NewBoolVar(name=f'travel_distance_{curricula_id}_{lb}_{ub}') for curricula_id in range(problem.num_curriculas) for lb,ub in periods_pairs}
    for curricula_id in range(problem.num_curriculas):
        for lb,ub in periods_pairs:
            model.Add(
                sum([
                    xvars[(course_id,lecture_id,room_id,lb)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
                !=sum([
                    xvars[(course_id,lecture_id,room_id,ub)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
            ).OnlyEnforceIf(travel_distance[(curricula_id,lb,ub)])

            model.Add(
                sum([
                    xvars[(course_id,lecture_id,room_id,lb)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
                ==sum([
                    xvars[(course_id,lecture_id,room_id,ub)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
            ).OnlyEnforceIf(travel_distance[(curricula_id,lb,ub)].Not())

    # 11. RoomSuitability: Some rooms may be not suitable for a given course because of the ab-
    # sence of necessary equipment (projector, amplification, . . . ). Each lecture of a course in an
    # unsuitable room counts as 1 violation.
    # Not needed in the udine problem- will be calculated without decision variables

    # 12. DoubleLectures: Some courses require that lectures in the same day are grouped together
    # (double lectures). For a course that requires grouped lectures, every time there is more than
    # one lecture in one day, a lecture non-grouped to another is not allowed. Two lectures are
    # grouped if they are adjacent and in the same room. Each non-grouped lecture counts as 1
    # violation.
    course_isolated_lectures={(course_id,lecture_id):model.NewBoolVar(name=f'_{course_id}_{lecture_id}') for course_id,lecture_id in problem.lectures}
    for course_id,lecture_id in problem.lectures:
        for day in range(problem.days):
            has_over_one_courses=model.NewBoolVar(name=f'over_one_courses_{course_id}_{day}_{period_id}')
            model.Add(
                sum([
                    xvars[(course_id,curr_lecture_id,room_id,period_id)]
                    for curr_lecture_id in range(problem.courses[course_id].letcures)
                    for room_id in range(problem.num_rooms)
                    for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                ])>1
            ).OnlyEnforceIf(has_over_one_courses)

            model.Add(
                sum([
                    xvars[(course_id,curr_lecture_id,room_id,period_id)]
                    for curr_lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                    for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                ])<=1
            ).OnlyEnforceIf(has_over_one_courses.Not())
            for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day):
                model.Add(
                    sum([
                        xvars[(course_id,curr_lecture_id,room_id,pcurr)]
                        for curr_lecture_id in [x for x in range(problem.lectures) if x!=lecture_id]
                        for room_id in range(problem.rooms)
                        for pcurr in [period_id-1,period_id+1]
                    ])
                    -sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for room_id in range(problem.num_rooms)
                    ])
                    +course_isolated_lectures[(course_id,lecture_id)]>=0
                ).OnlyEnforceIf(has_over_one_courses)
    
    objective=[
        sum([isolated_lectures[(course_id,lecture_id)] for course_id,lecture_id in problem.lectures]),
        sum([windows[(curricula_id,day,period_id)] for curricula_id in list(problem.curriculas.keys()) for day in range(problem.days) for period_id in range(problem.periods_per_day)]),
        sum([sum([room_stability[((course_id,room_id))] for room_id in range(problem.num_rooms)])-1 for course_id in range(problem.num_courses)]),
        sum([abs(student_min_max_load[(course_id,day,load)] * load-problem.min_daily_courses) if load<problem.min_daily_courses else problem.max_daily_lectures-load for course_id in range(problem.num_courses)  for day in range(problem.days) for load in range(0,problem.periods_per_day+1)]),
        sum([travel_distance[(curricula_id,lb,ub)] for curricula_id in range(problem.num_curriculas) for (lb,ub) in periods_pairs]),
        sum([course_isolated_lectures[(course_id,lecture_id)] for course_id,lecture_id in problem.lectures])
    ]

    model.Minimize(sum(objective))
    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=time_limit
    solver.parameters.num_search_workers=os.cpu_count()
    solver.parameters.log_search_process=True
    status=solver.Solve(model,cp_model.ObjectiveSolutionPrinter)
    esol={}
    if status==cp_model.FEASIBLE or status==cp_model.OPTIMAL:
        for (course_id,lecture_id,room_id,period_id),dvar in xvars.items():
            if solver.Value(dvar)==1:
                esol[(course_id,lecture_id)]=(problem.rooms[room_id].id,period_id)
    
    return esol

def cplex_cp_solver_formulation(problem,time_limit):
    model=cpx.CpoModel()
    xvars={(course_id,lecture_id,room_id,period_id):model.binary_var(name=f'dv_{course_id}_{lecture_id}_{room_id}_{period_id}') for course_id in range(problem.num_courses) for lecture_id in range(problem.courses[course_id].lectures) for room_id in range(problem.num_rooms) for period_id in range(problem.num_periods)}

    # 1. Setup a lecture in a single room without any constraint(period-room) violated
    for course_id in range(problem.num_courses):
        for lecture_id in range(problem.courses[course_id].lectures):
            for room_id in problem.courses[course_id].room_constraints:
                model.add(
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for period_id in range(problem.num_periods)
                    ])==0
                )
            
            for period_id in problem.courses[course_id].unavailability_constraints:
                model.add(
                    sum([
                        xvars[(course_id,room_id,room_id,period_id)]
                        for room_id in range(problem.num_rooms)
                    ])==0
                )

            model.add(
                sum([
                    xvars[(course_id,lecture_id,room_id,period_id)]
                    for room_id in range(problem.num_rooms)
                    for period_id in range(problem.num_periods)
                ])==1
            )
    
    # 2. Lectures of a course should not be placed in the same period(differs in the problem description(etc. laboratories of a course made by 2 lecturers))
    for course_id in range(problem.num_courses):
        for lecture_index1 in range(problem.courses[course_id].lectures):
            for lecture_index2 in range(lecture_index1+1,problem.courses[course_id].lectures):
                for period_id in range(problem.num_periods):
                    if period_id in problem.courses[course_id].unavailability_constraints: continue
                    model.add(
                        sum([
                            xvars[(course_id,lecture_index1,room_id,period_id)]
                            for room_id in range(problem.num_rooms)
                        ])
                        +sum([
                            xvars[(course_id,lecture_index2,room_id,period_id)]
                            for room_id in range(problem.num_rooms)
                        ])<=1
                    )
    
    # 3. At each period-room pair one lecture or no lecture should be placed
    for room_id in range(problem.num_rooms):
        for period_id in range(problem.num_rooms):
            model.add(
                sum([
                    xvars[(course_id,lecture_id,room_id,period_id)]
                    for course_id in range(problem.num_courses)
                    for lecture_id in range(problem.courses[course_id].lectures)
                ])<=1
            )
    
    # 4. Lecturers of the same curricula should not be placed in the same period
    for curricula_id in range(problem.num_curriculas):
        for course_index1 in range(len(problem.curriculas[curricula_id])):
            for course_index2 in range(lecture_index1+1,len(problem.curriculas[curricula_id])):
                for period_id in range(problem.num_periods):
                    if period_id in problem.courses[course_index1].unavailability_constraints or period_id in problem.courses[course_index2].unavailability_constraints: continue
                    model.add(
                        sum([
                            xvars[(problem.curriculas[curricula_id][course_index1],lecture_id,room_id,period_id)]
                            for lecture_id in range(problem.courses[course_index1].lectures)
                            for room_id in range(problem.num_rooms)
                        ])
                        +sum([
                            xvars[[problem.curriculas[curricula_id][course_index2],lecture_id,room_id,period_id]]
                            for lecture_id in range(problem.courses[course_index2].lectures)
                            for room_id in range(problem.num_rooms)
                        ])<=1
                    )
    
    # 6. Isolated lectures: Lectures belonging to a curriculum should be adja-
    # cent to each other (i.e., in consecutive periods). For a given curriculum we account for a
    # violation every time there is one lecture not adjacent to any other lecture within the same
    # day. Each isolated lecture in a curriculum counts as 1 violation.
    isolated_lectures={(course_id,lecture_id):model.binary_var(name=f'dv_{course_id}_{lecture_id}') for course_id in range(problem.num_courses) for lecture_id in range(problem.courses[course_id].lectures)}
    for course_id,lecture_id in problem.lectures:
        curricula_id=problem.find_curricula(course_id)
        for day in range(problem.days):
            for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day):
                model.add(
                    sum([
                        xvars[(curr_course_id,curr_lecturer_id,room_id,period_id-1)]
                        for curr_course_id in problem.curriculas[curricula_id]
                        for curr_lecturer_id in range()
                        for room_id in range(problem.num_rooms)
                    ])
                    -sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for room_id in range(problem.num_rooms)
                    ])
                    +sum([
                        xvars[(curr_course_id,curr_lecture_id,room_id,period_id+1)]
                        for curr_course_id in problem.curriculas[curricula_id]
                        for curr_lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                    ])
                    +isolated_lectures[(course_id,lecture_id)]>=0
                )
    
    # 7. Windows: Lectures belonging to a curriculum should not have time win-
    # dows (i.e., periods without teaching) between them. For a given curriculum we account for
    # a violation every time there is one windows between two lectures within the same day.
    # Each time window in a curriculum counts as many violation as its length (in periods).
    windows={(curricula_id,day,period_id):model.binary_var(name=f'windows_soft_violation_{curricula_id}_{day}_{period_id}') for curricula_id in list(problem.curriculas.keys()) for day in range(problem.days) for period_id in range(day*problem.periods_per_day+1,day*problem.periods_per_day+problem.periods_per_day-1)}
    for curricula_id in range(problem.num_curriculas):
        for day in range(problem.days):
            for period_id in range(day*problem.periods_per_day):
                has_previous_course=model.NewBoolVar(name=f'previous_course_{curricula_id}_{day}_{period_id}')
                cpx.if_then(
                    has_previous_course,
                    sum([
                        xvars[(course_id,lecture_id,room_id,previous_period)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[curricula_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for previous_period in range(day*problem.periods_per_day,period_id)
                    ])>=1
                )

                cpx.if_then(
                    has_previous_course==0,
                    sum([
                        xvars[(course_id,lecture_id,room_id,previous_period)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[curricula_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for previous_period in range(day*problem.periods_per_day,period_id)
                    ])==0
                )
                
                cpx.if_then(
                    windows[(curricula_id,day,period_id)],
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id-1)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                    ])
                    +has_previous_course==1
                )

                cpx.if_then(
                    windows[(curricula_id,day,period_id)]==0
                    ,sum([
                        xvars[(course_id,lecture_id,room_id,period_id-1)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                    ])
                    +has_previous_course!=1
                )
    
    # 8. Room stability: All lectures of a course should be given in the same room. Each distinct
    # room used for the lectures of a course, but the first, counts as 1 violation.
    room_stability={(course_id,room_id):model.NewBoolVar(name=f'course_{course_id}') for course_id in range(problem.num_courses) for room_id in range(problem.num_rooms)}
    for course_id in range(problem.num_courses):
        for room_id in range(problem.num_rooms):
            cpx.if_then(
                room_stability[(course_id,room_id)],
                sum([
                    xvars[(course_id,lecture_id,room_id,period_id)]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for period_id in problem.num_rooms
                ])==problem.courses[course_id].lectures
            )

            cpx.if_then(
                room_stability[(course_id,room_id)]==0,
                sum([
                    xvars[(course_id,lecture_id,room_id,period_id)]
                    for lecture_id in range(problem.num_rooms)
                    for period_id in range(day.problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                ])!=problem.courses[course_id].lectures
            )
    
    # 9. StudentMinMaxLoad: For each curriculum the number of daily lectures should be within a
    # given range. Each lecture below the minimum or above the maximum counts as 1 violation.e
    student_min_max_load = {(course_id,day,load):model.NewBoolVar(name=f'students_load_{course_id}_{day}_{load}') for course_id in range(problem.num_courses) for day in range(problem.days) for load in range(0,problem.periods_per_day+1)}
    for curricula_id in list(problem.curriculas.keys()):
        for day in range(problem.days):
            for load in range(0,problem.periods_per_day+1):
                cpx.if_then(
                    student_min_max_load[(curricula_id,day,load)],
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                    ])==load
                )
                
                cpx.if_then(
                    student_min_max_load[(curricula_id,day,load)]==0,
                    sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for course_id in problem.curriculas[curricula_id]
                        for lecture_id in range(problem.courses[course_id].lectures)
                        for room_id in range(problem.num_rooms)
                        for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                    ])!=load
                )

    # 10. TravelDistance: Students should have the time to move from one building to another one
    # between two lectures. For a given curriculum we account for a violation every time there
    # is an instantaneous move: two lectures in rooms located in different building in two adja-
    # cent periods within the same day. Each instantaneous move in a curriculum counts as 1
    # violation.
    # ** will be calculated without decision variable
    periods_pairs=[(period_id,period_id+1) for day in range(problem.days) for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day-1)]
    travel_distance = {(curricula_id, lb, ub):model.NewBoolVar(name=f'travel_distance_{curricula_id}_{lb}_{ub}') for curricula_id in range(problem.num_curriculas) for lb,ub in periods_pairs}
    for curricula_id in range(problem.num_curriculas):
        for lb,ub in periods_pairs:
            cpx.if_then(
                travel_distance[(curricula_id,lb,ub)],
                sum([
                    xvars[(course_id,lecture_id,room_id,lb)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
                !=sum([
                    xvars[(course_id,lecture_id,room_id,ub)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
            )

            cpx.if_then(
                travel_distance[(curricula_id,lb,ub)]==0,
                sum([
                    xvars[(course_id,lecture_id,room_id,lb)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
                ==sum([
                    xvars[(course_id,lecture_id,room_id,ub)]*room_id
                    for course_id in problem.curriculas[curricula_id]
                    for lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                ])
            )
    
    course_isolated_lectures={(course_id,lecture_id):model.NewBoolVar(name=f'_{course_id}_{lecture_id}') for course_id,lecture_id in problem.lectures}
    for course_id,lecture_id in problem.lectures:
        for day in range(problem.days):
            has_over_one_courses=model.binary_var(name=f'over_one_courses_{course_id}_{day}_{period_id}')
            cpx.if_then(
                has_over_one_courses
                ,sum([
                    xvars[(course_id,curr_lecture_id,room_id,period_id)]
                    for curr_lecture_id in range(problem.courses[course_id].letcures)
                    for room_id in range(problem.num_rooms)
                    for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                ])>1
            )

            cpx.if_then(
                has_over_one_courses==0
                ,sum([
                    xvars[(course_id,curr_lecture_id,room_id,period_id)]
                    for curr_lecture_id in range(problem.courses[course_id].lectures)
                    for room_id in range(problem.num_rooms)
                    for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day)
                ])<=1
            )

            for period_id in range(day*problem.periods_per_day,day*problem.periods_per_day+problem.periods_per_day):
                cpx.if_then(
                    has_over_one_courses
                    ,sum([
                        xvars[(course_id,curr_lecture_id,room_id,pcurr)]
                        for curr_lecture_id in [x for x in range(problem.lectures) if x!=lecture_id]
                        for room_id in range(problem.rooms)
                        for pcurr in [period_id-1,period_id+1]
                    ])
                    -sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for room_id in range(problem.num_rooms)
                    ])
                    +course_isolated_lectures[(course_id,lecture_id)]>=0
                )

                cpx.if_then(
                    has_over_one_courses==0
                    ,sum([
                        xvars[(course_id,curr_lecture_id,room_id,pcurr)]
                        for curr_lecture_id in [x for x in range(problem.lectures) if x!=lecture_id]
                        for room_id in range(problem.rooms)
                        for pcurr in [period_id-1,period_id+1]
                    ])
                    -sum([
                        xvars[(course_id,lecture_id,room_id,period_id)]
                        for room_id in range(problem.num_rooms)
                    ])
                    +course_isolated_lectures[(course_id,lecture_id)]<0
                )
    
    objective=[
        sum([isolated_lectures[(course_id,lecture_id)] for course_id,lecture_id in problem.lectures]),
        sum([windows[(curricula_id,day,period_id)] for curricula_id in list(problem.curriculas.keys()) for day in range(problem.days) for period_id in range(problem.periods_per_day)]),
        sum([sum([room_stability[((course_id,room_id))] for course_id in range(problem.num_courses) for room_id in range(problem.num_rooms)])]),
        sum([abs(student_min_max_load[(course_id,day,load)] * load-problem.min_daily_courses) if load<problem.min_daily_courses else problem.max_daily_lectures-load for course_id in range(problem.num_courses)  for day in range(problem.days) for load in range(0,problem.periods_per_day+1)]),
        sum([travel_distance[(curricula_id,lb,ub)] for curricula_id in range(problem.num_curriculas) for (lb,ub) in periods_pairs]),
        sum([course_isolated_lectures[(course_id,lecture_id)] for course_id,lecture_id in problem.lectures])
    ]

    model.minimize(sum(objective))

    params=cpx.CpoParameters()
    params.TimeLimit=time_limit
    params.Workers=os.cpu_count()
    params.LogVerbosity=True
    params.emphasis.mip=2
    solver=model.solve(params=params)
    esol={}
    if solver:
        for (course_id,lecture_id,room_id,period_id),dvar in xvars.items():
            if solver[dvar]==1:
                esol[(course_id,lecture_id)]=(room_id,period_id)
    return esol





# Dit solvers
def simulated_annealing(solution,time_limit=600):
    logger=logging.getLogger(f'Dit_Uoi_Debugger')
    logger.setLevel(logging.DEBUG)
    fh=logging.FileHandler(name=f'dit_file_logger.log',mode='w')
    sh=logging.StreamHandler()
    formatter=logging.Formatter(f'%(asctime)s\t%(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

    temperature=1000
    start_temperature=1000
    alpha=0.9999
    start_timer=time()
    freeze_temp=1.0
    last_improvement_counter=0
    LAST_IMPROVEMENT_LIMIT=1000000
    best_solution=solution.courses_solution
    best_cost=solution.compute_cost()
    while True:
        if time()-start_timer>time_limit:
            logger.info(f'Execution time exceeded\n')
            break
        
        moves=solution.get_moves()
        if len(moves)==0:
            continue
        
        memory={(course_id,lecture_id):solution.course_solution[(course_id,lecture_id)] for (course_id,lecture_id) in moves.keys()}
        current_solution_cost=solution.compute_cost()
        solution.reposition(moves)
        candicate_solution_cost=solution.compute_cost()
        if candicate_solution_cost<best_cost:
            best_solution=solution.courses_solution
            best_cost=candicate_solution_cost
            logger.info(f'New best solution found: Cost:{candicate_solution_cost}\tTemperature:{temperature}')
        elif candicate_solution_cost>best_cost:
            if random.uniform(0,1)>math.exp(temperature/(candicate_solution_cost-current_solution_cost)):
                logger.debug(f"Worse cost solution accepted\tSolution:{candicate_solution_cost}")
            else:
                solution.reposition(memory)
        else:
            solution.reposition(memory)
            last_improvement_counter+=1
        
        if last_improvement_counter>LAST_IMPROVEMENT_LIMIT:
            # Optimize a room or a teacher
            pass
        
        temperature*=alpha
        if temperature<freeze_temp:
            temperature=random.uniform(0.5,1.5)*start_temperature
            logger.info(f'Temperature:{temperature} reheated')
            # optimizer semester

    solution.reposition(best_solution)