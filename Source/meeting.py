from re import L
from Source.lecture import Lecture
from Source.classroom import Classroom

class Meeting:
    def __init__(self,m_id,m_start_hour,m_end_hour,m_day,m_course,m_semester,m_lecture):
        self.id=m_id
        self.start_hour=m_start_hour
        self.end_hour=m_end_hour
        self.day=m_day
        self.course=m_course
        self.semester=m_semester
        self.lecture=m_lecture

    def __iter__(self):
        self.meeting_notes=[self.id,self.start_hour,self.end_hour,self.course]
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
        return self.course.description()+"\n"+self.lecture.lecturer.name+"\n"+self.lecture.Ltype2String()+"("+self.lecture.classroom.id+")\n"

    def __str__(self):
        msg="ΑΝΑΓΝΩΡΙΣΤΙΚΟ:{}".format(self.id)+"\n"
        msg+="ΩΡΑ ΕΚΚΙΝΗΣΗΣ:{}".format(self.start_hour)+"\n"
        msg+="ΩΡΑ ΤΕΡΜΑΤΙΣΜΟΥ:{}".format(self.end_hour)+"\n"
        msg+="ΗΜΕΡΑ:{}".format(self.day)+"\n"
        msg+="ΜΑΘΗΜΑ:{}".format(self.course)+"\n"
        msg+="ΕΞΑΜΗΝΟ:{}".format(self.semester)+"\n"
        msg+="{}".format(str(self.lecture))+"\n"
        return msg

