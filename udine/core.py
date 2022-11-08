class Course:
    def __init__(self,lid,number_of_lectures,number_of_days_spread,number_of_students,building_id):
        self.lecturer_id=lid
        self.lectures=number_of_lectures
        self.days=number_of_days_spread
        self.students=number_of_students
        self.building_id=building_id
        self.unavailability_constraints=list()
        self.room_constraints=list()

    def __str__(self):
        return f'{self.lecturer_id=}\t{self.lectures=}\t{self.days=}\t{self.students=}\t{self.building_id}'

    def add_unavailability_constraint(self,period_id):
        self.unavailability_constraints.append(period_id)
    
    def add_room_constraint(self,room_id):
        self.room_constraints.append(room_id)

    @property
    def room_constraints(self):
        return self._room_constraints

    @property
    def unavailability_constraints(self):
        return self._unavailability_constraints 
        

class Room:
    def __init__(self,room_id,room_capacity,room_building_id):
        self.id=room_id
        self.capacity=room_capacity
        self.building_id=room_building_id

    def __str__(self):
        return f'{self.id=}\t{self.capacity=}\t{self.building_id}'