import os 
from collections import defaultdict

class Course:
    def __init__(self,course_id,lecturer_id,periods_spread_in,days_spread_in,number_of_students,bid):
        self.id=course_id
        self.lecturer=lecturer_id
        self.spread_periods=periods_spread_in
        self.spread_days=days_spread_in
        self.students=number_of_students
        self.building_id=bid
        self.period_unavailabilities=list()
        self.room_unavailabilities=list()

    def add_room_constraint(self,roomConstraint):
        self.room_unavailabilities.append(roomConstraint)
    
    def add_period_constraint(self,periodConstraint):
        self.period_unavailabilities.append(periodConstraint)

    def __eq__(self,course_id):
        return self.id==course_id

    def __str__(self) -> str:
        return f'Id:{self.id}\n Lecturer:{self.lecturer}\nSpread in:{self.spread_periods} periods\nSpread in:{self.spread_days} days\nStudents:{self.students}\nBuilding id:{self.building_id}\nPeriod unavailabilities:{len(self.period_unavailabilities)}\nRoom unavailabilities:{len(self.room_unavailabilities)}'

class Problem:
    path_to_datasets=os.path.join('','Datasets','udine_datasets')
    
    def __init__(self):
        self.courses=list()
        self.rooms=defaultdict(dict)
        self.curriculas=defaultdict(list)
        self.room_id=dict()
    
    def reset(self):
        self.courses.clear()
        self.rooms.clear()
        self.curriculas.clear()
    
    def number_of_rooms(self):
        return len(self.rooms)
    
    def number_of_courses(self):
        return len(self.courses)
    
    def number_of_curriculas(self):
        return len(self.curriculas)

    def read_instance(self,instance):
        self.reset()
        try:
            config_data=dict()
            category=None
            with open(os.path.join(Problem.path_to_datasets,instance),'r') as RF:
                for i,line in enumerate(RF):
                    if line=="END.": break
                    if i<9:
                        data=line.strip().split(':')
                        config_data[data[0]]=data[1]
                        continue
                    if line.strip()=="COURSES:":
                        category="COURSES"
                        continue
                    elif line.strip()=="ROOMS:":
                        category="ROOMS"
                        continue
                    elif line.strip()=="CURRICULAS:":
                        category="CURRICULA"
                        continue
                    elif line.strip()=="UNAVAILABILITY_CONSTRAINTS:":
                        category="UNAVAILABILITY_CONSTRAINTS"
                        continue
                    elif line.strip()=="ROOM_CONSTRAINTS:":
                        category="ROOM_CONSTRAINTS"
                        continue
                    
                    data=line.split()
                    if category=="Courses":
                        self.courses.append(Course(data[0],int(data[1].replace('t','')),int(data[2]),int(data[3]),int(data[4]),int(data[5])))
                    elif category=="ROOMS":
                        self.rooms[data[0]]['C']=int(data[1])
                        self.rooms[data[0]]['B']=int(data[2])
                    elif category=="CURRICULAS":
                        self.curriculas[data[0]]=[self.courses.index(data[i]) for i in range(2,len(data))]
                    elif category=="UNAVAILABILITY_CONSTRAINTS":
                        self.courses[self.courses.index(data[0])].add_period_constraint(int(data[1])*int(data[2]))
                    elif category=="ROOM_CONSTRAINTS":
                        self.courses[self.courses.index(data[0])].add_room_constraint(self.rooms.index(int(data[i])))
            self.create_rooms()

        except  FileNotFoundError:
            print(f'File {os.path.join(Problem.path_to_datasets,instance)} do not found')

    def create_rooms(self):
        if len(self.rooms)==0:
            raise ValueError("You did not provide the right amount of arguments in the room list")
        
        self.room_id=[i for i,(_,_) in self.rooms.items()]