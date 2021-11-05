class Classroom:
    def __init__(self,c_id,c_type,c_capacity):
        self.id=c_id
        self.type=c_type
        self.capacity=c_capacity
        self.locked=list()
    
    def __iter__(self):
        self.classroom_list=[self.id,self.capacity]
        self.id=-1
        return iter(self.classroom_list)
    
    def __next__(self):
        self.id+=1
        try:
            return self.classroom_list[self.id]
        except IndexError:
            self.id=0
            raise StopIteration
    
    def __eq__(self,oth) -> bool:
        return self.id==oth

    def add_course(self,course,timezone):
        self.locked.append((course,timezone))

    def move_to_timezone(self,course,timezone,exclude):
        for classroom_rec in self.locked:
            if classroom_rec in exclude: continue
            if classroom_rec==(course,timezone): return False
        return True

    def __str__(self):
        msg="Classroom Details\n"
        msg+="*"*8+"\n"
        msg+="ΑΝΑΓΝΩΡΙΣΤΙΚΟ:{}".format(self.id)+"\n"
        msg+="ΕΙΔΟΣ:{}".format(self.type)+"\n"
        msg+="ΧΩΡΙΤΗΚΟΤΗΤΑ:{}".format(self.capacity)+"\n"
        return msg

    

    
