import random 

class Course:
    def __init__(self,course_id,course_name,course_semester,course_hours_theory,course_hours_lab,hours_tutoring):
        self.id=course_id
        self.name=course_name
        self.semester=course_semester
        self.theory_hours=course_hours_theory
        self.lab_hours=course_hours_lab
        self.tutoring_hours=hours_tutoring
        self.course_laboratory_instances=random.randint(4,10)
        self.lecturers=[(self.id,lecture_id) for lecture_id in range(0,self.theory_hours+self.lab_hours+self.tutoring_hours)]
        self.unavailability_constraints=list()
        self.room_constraints=list()
        self.lecturer=None
    
    def add_unavailability_constraints(self,period_id):
        self.unavailability_constraints.append(period_id)
    
    def add_room_constraint(self,room_id):
        self.room_constraints.append(room_id)

    def to_list(self):
        return [self.semester,self.theory_hours,self.lab_hours,self.tutoring_hours]

    @property
    def laboratory(self):
        return [(self.id,self.lab_hours+self.tutoring_hours+i) for i in range(self.course_laboratory_instances)]

    @property
    def theory(self):
        return [(self.id,lecture_id) for lecture_id in range(self.theory_hours)]
    
    @property
    def tutoring(self):
        return [(self.id,self.theory_hours+i) for i in range(self.tutoring_hours)]

class Lecturer:
    def __init__(self,lecturer_name,lecturer_mail,lecturer_user_name):
        self.name=lecturer_name.upper()
        self.email=lecturer_mail
        self.user_name=lecturer_user_name
        self.lectures=list()
        self.laboratories=list()
        self.lecturer_constraints=list()
        self.lecturer_history=list()
    
    def __eq__(self,lecturer):
        return self.name==lecturer.name

    def add_constraint(self,period_id):
        self.lecturer_constraints.append(period_id)
    
    def add_lecturer_history(self,course_id,lecture_id,period_id):
        self.history.append((course_id,lecture_id,period_id))
    
    def add_lecture(self,course_id,lecture_id):
        self.lectures.append((course_id,lecture_id))
    
    def add_laboratory(self,course_id,lecture_id):
        self.laboratories.append((course_id,lecture_id))
    
    def to_list(self):
        return [self.id,self.email,self.user_name]
    
class Room:
    def __init__(self,room_id,room_type_id,room_capacity):
        self.id=room_id
        self.room_type=room_type_id
        self.capacity=room_capacity
        self.equipment=list()

    def add_equipment(self,equipment_id):
        self.equipment.append(equipment_id)
    
    def to_list(self):
        return [self.id,self.room_type,self.capacity]
    
    def __str__(self):
        output=f"Room:{self.id}\n"
        output+=f"Capacity:{self.capacity}\n"
        output+=f"Equipment:{', '.join([str(x) for x in self.equipment])}\n"
        return output

class Assignment:
    def __init__(self,assignment_course_name,assignment_lecturer_name,assignment_hours_per_lab,assignment_laboratory_number): 
        self.course_name=assignment_course_name
        self.lecturer_name=assignment_lecturer_name
        self.periods_per_lab=assignment_hours_per_lab
        self.labs=assignment_laboratory_number