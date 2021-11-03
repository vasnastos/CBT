class Semester:
    days=['ΔΕΥΤΕΡΑ','ΤΡΙΤΗ','ΤΕΤΑΡΤΗ','ΠΕΜΠΤΗ','ΠΑΡΑΣΚΕΥΗ']
    timezone=['08:00-09:00','09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00','17:00-18:00','18:00-19:00','19:00-20:00','20:00-21:00']
   
    def __init__(self,semester):
        self.id=semester
        self.meetings=dict()
        for day in Semester.days:
            self.meetings[day]=list()

    def add_meeting(self,meeting):
        self.meetings[meeting.day].append(meeting)

    def __eq__(self, o:str) -> bool:
        return self.id==o