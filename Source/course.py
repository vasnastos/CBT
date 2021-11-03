class Course:
    def __init__(self,c_id,c_title,c_semester,c_flow,c_hours_theory,c_hours_tutoring,c_hours_lab,c_credits):
        self.id=c_id
        self.title=c_title.strip()
        self.semester=c_semester
        self.flow=c_flow
        self.hours_theory=c_hours_theory
        self.hours_tutoring=c_hours_tutoring
        self.hours_lab=c_hours_lab
        self.credits=c_credits
        self.enrollments=0
        self.course_list=list()
    
    def __iter__(self):
        self.course_list=[self.id,self.title,self.semester,self.hours_theory,self.hours_tutoring,self.hours_lab,self.credits,self.enrollments]
        self.i=-1
        return iter(self.course_list)
    
    def __next__(self):
        self.id+=1
        try:
            return self.course_list[self.id]
        except IndexError:
            self.id=0
            raise StopIteration
    
    def __eq__(self,oth):
        return self.title+"_"+str(self.semester)==oth

    def get_semester(self):
        if self.flow=="-": return str(self.semester)
        return str(self.semester)+"-"+self.flow
    
    def description(self):
        return self.title+"("+self.id+")"
    
    def __str__(self):
        msg="ΑΝΑΓΝΩΡΙΣΤΙΚΟ:{}".format(self.id)+"\n"
        msg+="ΤΙΤΛΟΣ ΜΑΘΗΜΑΤΟΣ:{}".format(self.title)+"\n"
        msg+="ΕΞΑΜΗΝΟ:{}".format(self.semester)+"\n"
        msg+="ΩΡΕΣ ΘΕΩΡΙΑΣ:{}".format(self.hours_theory)+"\n"
        msg+="ΩΡΕΣ ΕΡΓΑΣΤΗΡΙΟΥ:{}".format(self.hours_lab)+"\n"
        msg+="ΩΡΕΣ ΕΝΙΣΧΥΤΙΚΗΣ ΔΙΔΑΣΚΑΛΙΑΣ:{}".format(self.hours_tutoring)+"\n"
        msg+="ΔΙΔΑΚΤΙΚΕΣ ΜΟΝΑΔΕΣ:{}".format(self.credits)+"\n"
        msg+="ΕΓΓΡΑΦΕΣ:{}".format(self.enrollments)+"\n"
        return msg
