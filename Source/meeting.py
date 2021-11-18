from Source.lecture import Lecture
from Source.classroom import Classroom

class Meeting:
    timezones=['08:00-09:00','09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00','17:00-18:00','18:00-19:00','19:00-20:00','20:00-21:00']
    def __init__(self,m_start_hour,m_end_hour,m_day,m_semester,m_course,m_lecturer,m_classroom):
        self.start_hour=m_start_hour
        self.end_hour=m_end_hour
        self.day=m_day
        self.semester=m_semester
        end_int_hour=int(self.end_hour.split(':')[0])
        start_int_hour=int(self.start_hour.split(':')[0])
        self.duration=end_int_hour-start_int_hour
        self.course=m_course
        self.lecturer=m_lecturer
        self.classroom=m_classroom
        self.meetings=list()
<<<<<<< HEAD

=======
        
>>>>>>> 06477f7ac76116bd2267277be186576b29cdc5f5
    def __iter__(self):
        self.meeting_notes=[self.id,self.start_hour,self.end_hour]
        self.meeting_notes.extend(list(iter(self.course)))
        self.meeting_notes.extend(list(iter(self.lecture)))
        self.id=-1
        return iter(self.meeting_notes)

    def __next__(self):
        self.id+=1
        try:
            return self.meeting_notes[self.id]
        except IndexError:
            self.id=0
            return StopIteration
    
    def description(self):
        return self.course.description()+"\n"+self.lecturer.name+"\n"+self.lecture.Ltype2String()+"("+self.classroom.id+")\n"

    def timezone(self):
        periods=list()
        meeting_initial_hour=int(self.start_hour.split(':')[0])
        meeting_end_hour=int(self.end_hour.split(':')[0])
        for timezone in Meeting.timezones:
            zone_to_hour_system=timezone.split('-')
            zone_start_hour=int(zone_to_hour_system[0].split(':')[0])
            zone_end_hour=int(zone_to_hour_system[1].split(':')[0])
            if zone_start_hour>=meeting_initial_hour and zone_end_hour<=meeting_end_hour:
                periods.append(timezone)
        return periods

    def get_semester(self):
        return self.course.get_semester()

    def __str__(self):
        msg="ΑΝΑΓΝΩΡΙΣΤΙΚΟ:{}".format(self.id)+"\n"
        msg+="ΩΡΑ ΕΚΚΙΝΗΣΗΣ:{}".format(self.start_hour)+"\n"
        msg+="ΩΡΑ ΤΕΡΜΑΤΙΣΜΟΥ:{}".format(self.end_hour)+"\n"
        msg+="ΗΜΕΡΑ:{}".format(self.day)+"\n"
        msg+="ΜΑΘΗΜΑ:{}".format(self.course)+"\n"
        msg+="ΕΞΑΜΗΝΟ:{}".format(self.semester)+"\n"
        msg+="{}".format(str(self.lecture))+"\n"
        return msg

