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
    EXT=6


class Lecturer:
    def __init__(self,l_id,l_name,l_mail,l_rank):
        self.identifier=l_id
        self.name=l_name
        self.mail=l_mail
        self.rank=Rank(int(l_rank))
<<<<<<< HEAD
        self.meetings=dict()
=======
        self.lectures=dict()
>>>>>>> 06477f7ac76116bd2267277be186576b29cdc5f5
    
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
       msg="ΑΝΑΓΝΩΡΙΣΤΙΚΟ:{}".format(self.identifier)+"\n"
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
        elif name=="ΕΚΤΑΚΟΣ":
            return Rank.EXT
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
    
    def set_lecturer_meetings(self,lecturer_meetings):   
        for meeting in lecturer_meetings:
            if meeting[5] not in self.meetings:
                self.meetings[meeting[5]]=list()
            self.meetings[meeting[5]].append((meeting[0],meeting[1],meeting[2],meeting[3],meeting[4],meeting[6]))

    def lecturer_validation(self):
        validate=list()
        for day in Constant.days:
            if day not in self.meetings: continue
            valid=True
            for meeting in self.meetings[day]:
                for meeting1 in self.meetings[day]:
                    if meeting==meeting1: continue
                    start_hour_meeting=int(meeting[3].strip().split(':')[0])
                    end_hour_meeting=int(meeting[4].strip().split(':')[0])
                    start_hour_meeting_1=int(meeting1[3].strip().split(':')[0])
                    if start_hour_meeting==start_hour_meeting_1 or start_hour_meeting<=start_hour_meeting_1<end_hour_meeting:
                        valid=False
                        break
            if valid==False:
                break
            validate.append(valid)
        return len([valid for valid in validate if valid])==len(self.meetings)        
                            