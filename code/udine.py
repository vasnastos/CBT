
class Lecturer:
    def __init__(self,lid):
        self.lecturer_id=lid
        self.courses=list()

    def __eq__(self,lid):
        return self.lecturer_id==lid

    def add_course(self,course_obj):
        self.courses.append(course_obj)

    def __list__(self):
        return [self.lecturer_id,'-'.join([course.course_id for course in self.courses])]

    def __str__(self):
        msg=super().__str__()+'\n'
        msg+="Courses\n"
        msg+="\n".join([str(course) for course in self.courses])
        return msg


class Course:
    def __init__(self,cid,lecturer_id,number_of_meetings,days_to_be_done,cstudents,building_id):
        self.course_id=cid
        self.lecturer=lecturer_id
        self.lectures=number_of_meetings
        self.periods_to_take_place=days_to_be_done
        self.students=cstudents
        self.building=building_id
        self.lecture_id=1

    def set_lecturer(self,lecturer):
        self.lecturer=lecturer
    
    def get_lecture_id(self):
        retrieved_id=self.lecture_id
        self.lecture_id+=1
        return f"{self.course_id}_{retrieved_id}"

    def __eq__(self,cid):
        return self.course_id==cid
    
    def __list__(self):
        return [self.course_id,self.lecturer,self.lectures,self.periods_to_take_place,self.students,self.building]

    def __str__(self):
        return f"Id:{self.course_id}\n#Lectures{self.lectures}\nSpreading Periods:{self.periods_to_take_place}\n#Students:{self.students}\nBuilding id:{self.building}"

class Classroom:
    types_of_building={
        "ΑΜΦΙΘΕΑΤΡΟ":0,
        "ΕΡΓΑΣΤΗΡΙΟ":1
    }

    def __init__(self,rid,rcapacity,rbid):
        self.room_id=rid
        self.capacity=rcapacity
        self.building_id=rbid
    
    def __list__(self):
        return [self.room_id,self.capacity,self.building_id]
    
    def __str__(self):
        return f"Id:{self.room_id}\nCapacity:{self.capacity}\nType:{self.building_id}"

class Curricula:
    def __init__(self,cid):
        self.curricula_id=cid
        self.courses=list()
    
    def add_course(self,course_instance):
        self.course.append(course_instance)
    
    def is_curricula_of(self,course_id):
        return course_id in self.courses

    def __eq__(self,qid):
        return self.curricula_id==qid
    
    def __list__(self):
        return [self.curricula_id,'-'.join([course.course_id for course in self.courses])]

    def __str__(self):
        msg=f"Curricula:{self.curricula_id}\n"
        msg+="\n".join([str(course) for course in self.courses])
        msg+='\n\n'
        return msg


class Meeting:
    def __init__(self,mid,course_id):
        self.meeting_id=mid
        self.course=course_id
        self.day=-1
        self.period_of_day=-1
        self.period_constraints=list()
        self.room_constraints=list()
    
    def set_period(self,pday,period):
        self.day=pday
        self.period_of_day=period
    
    def add_constraint(self,constraint:tuple,constraint_for='period'):
        if constraint_for=='period':
            self.period_constraints.append(constraint)
        elif constraint_for=='room':
            self.room_constraints.append(constraint)
    
    def is_feasible(self,period_pair):
        return period_pair not in self.period_constraints

    def __list__(self):
        return [self.meeting_id,self.course,self.day,self.period_of_day," ".join([f"({day},{period})" for day,period in self.period_constraints])," ".join([f"{room_id}" for room_id in self.room_constraints])]

    def __str__(self):
        return f"Id:{self.meeting_id}\nCourse:{self.course}\nDay:{self.day}\nPeriod_of_period:{self.period_of_day}"
