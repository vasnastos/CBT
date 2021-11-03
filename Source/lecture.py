from enum import Enum
from Source.classroom import Classroom
from Source.lecturer import Lecturer

class LType(Enum):
    THEORY=1
    LABORATORY=2
    PRIVATE_TUTORING=3
    ASSISTANTSHIP=4


class Lecture:
    def __init__(self,l_type,l_duration,l_classroom,l_lecturer):
        self.ltype=Lecture.string2Ltype(l_type)
        self.duration=l_duration
        self.classroom=l_classroom
        self.lecturer=l_lecturer
        self.available_classrooms=list()
    
    def __iter__(self):
        self.lecturer_list=[self.ltype.name,self.duration]
        self.lecturer_list.extend(list(iter(self.classroom)))
        self.lecturer_list.extend(list(iter(self.lecturer)))
        self.id=-1
        return iter(self.lecturer_list)
    
    def __next__(self):
        self.id+=1
        try:
            self.lecturer_list[self.id]
        except IndexError:
            self.id=0
            raise StopIteration

    def add_available_classroom(self,class_id:str): 
        self.add_available_classroom(class_id)

    def __str__(self):
        msg="ΤΥΠΟΣ ΠΑΡΑΔΟΣΗΣ:{}".format(self.ltype.name)
        msg+="ΔΙΑΡΚΕΙΑ:{}".format(self.duration)+"\n"
        msg+="ΑΙΘΟΥΣΑ ΔΙΔΑΣΚΑΛΙΑΣ\n"+"*"*9+"\n"
        msg+=str(self.classroom)
        msg+="ΔΙΔΑΣΚΩΝ\n"+"*"*9+"\n"
        msg+=str(self.lecturer)
        return msg
    
    @staticmethod
    def string2Ltype(name:str)->LType:
        if name=="ΔΙΑΛΕΞΗ":
            return LType.THEORY
        elif name=='ΦΡΟΝΤΗΣΤΗΡΙΟ':
            return LType.PRIVATE_TUTORING
        elif name=="ΕΡΓΑΣΤΗΡΙΟ":
            return LType.LABORATORY
        else:
            return LType.ASSISTANTSHIP
    
    def Ltype2String(self):
        if self.ltype==LType.THEORY:
            return "ΔΙΑΛΕΞΗ"
        elif self.ltype==LType.LABORATORY:
            return "ΕΡΓΑΣΤΗΡΙΟ"
        elif self.ltype==LType.PRIVATE_TUTORING:
            return "ΦΡΟΝΤΗΣΤΗΡΙΟ"
        else:
            return "ΑΣΚΗΣΗ ΠΡΑΞΗΣ"
