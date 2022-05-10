from tabulate import tabulate

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

    def _tabulate_(self):
        print(f'Lecturer:{self.lecturer_id}')
        print(f'Lecturer Courses:{len(self.courses)}')
        print('-'*10)
        print(tabulate([[course.course_id,course.students] for course in self.courses],headers=['COURSE ID','STUDENTS'],tablefmt='fancy_grid'),end='\n\n')


    def __str__(self):
        msg=self.lecturer_id+'\n'
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
        self._curricula=None

    def set_lecturer(self,lecturer):
        self.lecturer=lecturer
    
    def get_lecture_id(self):
        retrieved_id=self.lecture_id
        self.lecture_id+=1
        return f"{self.course_id}_{retrieved_id}"

    @property
    def curricula(self):
        return self._curricula
    
    @curricula.setter
    def curricula(self,curricula_id):
        self._curricula=curricula_id        

    def __eq__(self,cid):
        return self.course_id==cid
    
    def __list__(self):
        return [self.course_id,self.lecturer,self.lectures,self.periods_to_take_place,self.students,self.building]

    def __str__(self):
        return f"Id:{self.course_id}\n#Lectures{self.lectures}\nSpreading Periods:{self.periods_to_take_place}\n#Students:{self.students}\nBuilding id:{self.building}"

class Classroom:
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
        self.C=len(self.courses)
    
    def add_course(self,course_instance):
        self.courses.append(course_instance)
        self.C=len(self.courses)

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
    
    def _tabulate_(self):
        print(f'Curricula id:{self.curricula_id}')
        print(f'Courses:{self.C}')
        print(tabulate([[course.course_id,course.students] for course in self.courses],headers=['COURSE ID','STUDENTS'],tablefmt='fancy_grid'))


class Meeting:
    def __init__(self,mid,course_id):
        self.meeting_id=mid
        self.course=course_id
        self._lecturer=None
        self._curricula=None
        self.day=-1
        self.period_of_day=-1
        self.period_constraints=list()
        self.room_constraints=list()
    
    def set_period(self,pday,period):
        self.day=pday
        self.period_of_day=period
    
    @property
    def lecturer(self):
        return self._lecturer

    @lecturer.setter
    def lecturer(self,lecturer_object):
        self._lecturer=lecturer_object

    @property
    def curricula(self):
        return self._curricula
    
    @curricula.setter
    def curricula(self,curricula_obj):
        self._curricula==curricula_obj

    def add_constraint(self,constraint:tuple,constraint_for='period'):
        if constraint_for=='period':
            self.period_constraints.append(constraint)
        elif constraint_for=='room':
            self.room_constraints.append(constraint)
    
    def is_feasible(self,checkval,feasibility_for='period'):
        return checkval not in self.period_constraints if feasibility_for=='period' else checkval not in self.room_constraints if feasibility_for=='room' else False

    def is_neighbor_meeting(self,meeting):
        return self.lecturer==meeting.lecturer or self.curricula==meeting.curricula

    def __list__(self):
        return [self.meeting_id,self.course,self.day,self.period_of_day," ".join([f"({day},{period})" for day,period in self.period_constraints])," ".join([f"{room_id}" for room_id in self.room_constraints])]

    def __str__(self):
        return f"Id:{self.meeting_id}\nCourse:{self.course}\nDay:{self.day}\nPeriod_of_period:{self.period_of_day}"

    def _tabulate_(self):
        print(f'Meeting_id:{self.meeting_id}')  
        print(f'Course:{self.course_id}')
        print(f'Lecturer:{self.course}')
