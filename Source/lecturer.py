from enum import Enum
from prettytable import PrettyTable
from prettytable.prettytable import ALL
from Source.constant_vars import Constant

class Rank(Enum):
    DEP=0
    EDIP=1
    PY=2
    YADE=3
    PHD=4
    TEACHING_ASSISTANT=5


class Lecturer:
    def __init__(self,l_id,l_name,l_mail,l_rank):
        self.identifier=l_id
        self.name=l_name
        self.mail=l_mail
        self.rank=Lecturer.string2Rank(l_rank)
        self.lectures=dict()
    
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

    def add_job(self,day,course,timezone):
        if day not in self.lectures:
            self.lectures[day]=dict()
        else:
            if timezone in self.lectures[day]:
                return
        self.lectures[day][timezone]=course

    def __eq__(self,othername):
        return self.identifier==othername
    
    def equals(self,oth):
        return self.identifier==oth.identifier

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
    
    def info(self):
        table=PrettyTable()
        table.hrules=ALL
        fieldnames=[' ']
        fieldnames.extend(Constant.days)
        table.field_names=fieldnames
        widths={name:30 for name in fieldnames}
        table._max_width=widths
        for timezone in Constant.timezones:
            row=list()
            row.append(timezone)
            for day in Constant.days:
                description=""
                if day in self.lectures:
                    if timezone in self.lectures[day]:
                        description+=self.lectures[day][timezone]
                row.append(description)
            table.add_row(row)
        print(table,end='\n\n')

    