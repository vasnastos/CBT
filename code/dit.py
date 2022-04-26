from enum import Enum

class Rank(Enum):
    DEP=1,
    EDIP=2,
    PY=3

class Building(Enum):
    AMFITHEATER=0,
    LABORATORY=1

class Lecturer:
    auto_id=1

    def __init__(self,lname,lmail,lrank_id,autoincrement=False,**args):
        self.lecturer_id=Lecturer.auto_id if autoincrement else args.get('lecturer_id',-1)
        if autoincrement:
            self.auto_id+=1
        self.name=lname
        self.email=lmail
        self.rank=Rank(lrank_id)
    
    def __str__(self):
        return f"Id:{self.lecturer_id}\nName:{self.name}\nemail:{self.email}\nRank:{self.rank._name_}"
    
class Course:
    def __init__(self,cid,cname,cflow,th_hours,lab_hours,pt_hours,course_credits):
        self.course_id=cid
        self.title=cname
        self.flow=cflow
        self.theory_hours=th_hours
        self.laboratory_hours=lab_hours
        self.private_tutoring_hours=pt_hours
        self.credits=course_credits
    
    def __str__(self):
        return f"Id:{self.course_id}\nTitle:{self.title}\nFlow:{self.flow}\nTheory Hours:{self.theory_hours}\nLaboratory hours:{self.laboratory_hours}\nPrivate tutoring hours:{self.private_tutoring_hours}\nCredits:{self.credits}\n"

class Classroom:
    types_of_building={
        "ΑΜΦΙΘΕΑΤΡΟ":0,
        "ΕΡΓΑΣΤΗΡΙΟ":1
    }

    def __init__(self,rid,rcapacity,rbid):
        self.room_id=rid
        self.capacity=rcapacity
        self.building_id=Building(Classroom.types_of_building[rbid])
    
    def __str__(self):
        return f"Id:{self.room_id}\nCapacity:{self.capacity}\nType:{self.building_id._name_}"

class Curricula:
    def __init__(self,cid):
        self.curricula_id=cid
        self.courses=list()
    
    def add_course(self,course_instance):
        self.course.append(course_instance)
    
    def __str__(self):
        msg=f"Curricula:{self.curricula_id}\n"
        msg+="\n".join([str(course) for course in self.courses])
        msg+='\n\n'
        return msg