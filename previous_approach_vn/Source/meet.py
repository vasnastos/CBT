class Meeting:
    def __init__(self,m_start_hour,m_end_hour,m_day,m_semester):
        self.start_hour=m_start_hour
        self.end_hour=m_end_hour
        self.day=m_day
        self.semester=m_semester
        start_int_hour=int(self.start_hour.split(':')[0])
        end_int_hour=int(self.end_hour.split(':')[0])
        self.duration=end_int_hour-start_int_hour
    
    def set_lecture(self,a_lecture):
        self.lecture=a_lecture
    
    def description(self):
        return self.lecture.course.description()+'\n'+self.lecture.lecturer.name+'\n'+self.lecture.Ltype2String()+'('+self.lecture.classroom.id+')\n'
    
    def get_semester(self):
        return self.lecture.course.get_semester()
    
    def __str__(self):
        msg="ΩΡΑ ΕΚΚΙΝΗΣΗΣ:{}".format(self.start_hour)+"\n"
        msg+="ΩΡΑ ΤΕΡΜΑΤΙΣΜΟΥ:{}".format(self.end_hour)+"\n"
        msg+="ΗΜΕΡΑ:{}".format(self.day)+"\n"
        msg+="ΜΑΘΗΜΑ:{}".format(self.course)+"\n"
        msg+="ΕΞΑΜΗΝΟ:{}".format(self.semester)+"\n"
        msg+="{}".format(str(self.lecture))+"\n"
        return msg

