class Classroom:
    def __init__(self,c_id,c_type,c_capacity):
        self.id=c_id
        self.type=c_type
        self.capacity=c_capacity
    
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
    
    def __str__(self):
        msg="Classroom Details\n"
        msg+="*"*8+"\n"
        msg+="ΑΝΑΓΝΩΡΙΣΤΙΚΟ:{}".format(self.id)+"\n"
        msg+="ΕΙΔΟΣ:{}".format(self.type)+"\n"
        msg+="ΧΩΡΙΤΗΚΟΤΗΤΑ:{}".format(self.capacity)+"\n"
        return msg

    def __eq__(self,oth) -> bool:
        return self.id==oth

    
