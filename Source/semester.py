from Source.lecture import LType

class Semester:
    days=['ΔΕΥΤΕΡΑ','ΤΡΙΤΗ','ΤΕΤΑΡΤΗ','ΠΕΜΠΤΗ','ΠΑΡΑΣΚΕΥΗ']
    timezones=['08:00-09:00','09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00','17:00-18:00','18:00-19:00','19:00-20:00','20:00-21:00']
   
    def __init__(self,semester):
        self.id=semester
        self.meetings=dict()
        for day in Semester.days:
            self.meetings[day]=list()
        self.meetings_raw=list()
        self.courses=list()
        self.lock_timezones=set()

    def add_meeting(self,meeting):
        self.meetings[meeting.day].append(meeting)
        self.meetings_raw.append(meeting)

    def add_course(self,course):
        self.courses.append(course)

    def lock_timezones(self):
        for timezone in Semester.timezones:
            pass
    
    def course_validance(self,course):
        course_hours={
            LType.THEORY:0,
            LType.LABORATORY:0,
            LType.PRIVATE_TUTORING:0
        }
        lab_found=False
        for meeting in self.meetings_raw:
            if meeting.course.equals(course):
                if meeting.lecture.ltype==LType.LABORATORY:
                    if lab_found==False:
                        course_hours[LType.LABORATORY]+=course.lab_hours
                        lab_found=True
                    else: continue
                elif meeting.lecture.ltype==LType.ASSISTANTSHIP:
                    course_hours[LType.THEORY]+=meeting.duration
                else:
                    course_hours[meeting.lecture.ltype]+=meeting.duration
        if not (course.theory_hours==course_hours[LType.THEORY] and course.lab_hours==course_hours[LType.LABORATORY] and course.tutoring_hours==course_hours[LType.PRIVATE_TUTORING]):
            print(course.theory_hours,course_hours[LType.THEORY])
            print(course.lab_hours,course_hours[LType.LABORATORY])
            print(course.tutoring_hours,course_hours[LType.PRIVATE_TUTORING])
            print(course.title)
        return course.theory_hours==course_hours[LType.THEORY] and course.lab_hours==course_hours[LType.LABORATORY] and course.tutoring_hours==course_hours[LType.PRIVATE_TUTORING]

    def semester_validance(self):
        validation_counter=0
        for course in self.courses:
            validation=self.course_validance(course)
            if validation:
                validation_counter+=1
        return validation_counter==len(self.courses)

    def __eq__(self, o:str) -> bool:
        return self.id==o