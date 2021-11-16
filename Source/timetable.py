from Source.database import Cbt_database

class Timetable:
    def __init__(self):
        self.db=Cbt_database('cbt_base.db')
        self.meetings=self.db.meetings()
        self.lecturers=self.db.lecturers()
        self.lectures=self.db.lectures()
        self.courses=self.db.courses()
    
    def print_all(self):
        print(len(self.lectures))
        print(len(self.lecturers))
        print(len(self.courses))
        print(len(self.meetings))

    def timetable_cost(self):
        pass