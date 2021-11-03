from enum import Enum

class Rank(Enum):
    DEP=0
    EDIP=1
    PY=2
    YADE=3
    PHD=4
    TEACHING_ASSISTANT=5


class Lecturer:
    def __init__(self,l_id,l_name,l_mail,l_rank):
        self.id=l_id
        self.name=l_name
        self.mail=l_mail
        self.rank=Lecturer.string2Rank(l_rank)
    
    def __iter__(self):
        self.lecturer_list=[self.id,self.name,self.rank.name]
        self.id=-1
        return iter(self.lecturer_list)

    def __next__(self):
        self.id+=1
        try:
            return self.lecturer_list[self.id]
        except IndexError:
           self.id=0
           raise StopIteration

    def __eq__(self,othername):
        return self.id==othername

    def __str__(self):
       msg="ΑΝΑΓΝΩΡΙΣΤΙΚΟ:{}".format(self.id)+"\n"
       msg+="ΟΝΟΜΑ:{}".format(self.name)+"\n"
       msg+="ΗΛΕΚΤΡΟΝΙΚΗ ΔΙΕΥΘΥΝΣΗ:{}".format(self.mail)+"\n"
       msg+="ΒΑΘΜΙΔΑ:{}".format(self.rank.name)+"\n"
       return msg

    @staticmethod
    def string2Rank(name:str)->Rank:
        if name=="ΔΕΠ":
            return Rank.DEP
        elif name=="ΕΔΙΠ":
            return Rank.EDIP
        elif name=="ΥΑΔΕ":
            return Rank.YADE
        elif name=="ΠΥ":
            return Rank.PY
        elif name=="ΥΠΟΨΗΦΙΟΣ ΔΙΔΑΚΤΟΡΑΣ":
            return Rank.PHD
        else:
            return Rank.TEACHING_ASSISTANT
    

# TEST
# l=Lecturer(190,"Christos Gkogkos",Rank.DEP)
# lecturer_info=list(iter(l))
# print(lecturer_info)

    