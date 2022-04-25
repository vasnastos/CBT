import termcolor
from Source.lecture import LType
import os
import xlsxwriter

class Semester:
    days=['ΔΕΥΤΕΡΑ','ΤΡΙΤΗ','ΤΕΤΑΡΤΗ','ΠΕΜΠΤΗ','ΠΑΡΑΣΚΕΥΗ']
    timezones=['08:00-09:00','09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00','17:00-18:00','18:00-19:00','19:00-20:00','20:00-21:00']
   
    def __init__(self,semester):
        self.id=semester
        self.meetings=dict()
        for day in Semester.days:
            self.meetings[day]=list()
        self.meetings_raw=list()
        self.courses=list()
        self.locked_timezones={day:set() for day in Semester.days}
        self.semester_penalty=0

    def add_meeting(self,meeting):
        self.meetings[meeting.day].append(meeting)
        self.meetings_raw.append(meeting)

    def add_course(self,course):
        self.courses.append(course)

    def lock_timezones(self):
        for timezone in Semester.timezones:
            for meeting in self.meetings_raw:
                self.get_lock_timezones(meeting.start_hour+"-"+meeting.end_hour,meeting.day)
    
    def course_validance(self,course):
        course_hours={
            LType.THEORY:0,
            LType.LABORATORY:0,
            LType.PRIVATE_TUTORING:0
        }
        lab_found=False
        for meeting in self.meetings_raw:
            if meeting.lecture.course.equals(course):
                if meeting.lecture.ltype==LType.LABORATORY:
                    if lab_found==False:
                        course_hours[LType.LABORATORY]+=course.lab_hours
                        lab_found=True
                    else: continue
                elif meeting.lecture.ltype==LType.ASSISTANTSHIP:
                    course_hours[LType.THEORY]+=meeting.duration
                else:
                    course_hours[meeting.lecture.ltype]+=meeting.duration
        if not (course.theory_hours==course_hours[LType.THEORY] and course.lab_hours==course_hours[LType.LABORATORY] and course.tutoring_hours==course_hours[LType.PRIVATE_TUTORING]):
            print(course.theory_hours,course_hours[LType.THEORY])
            print(course.lab_hours,course_hours[LType.LABORATORY])
            print(course.tutoring_hours,course_hours[LType.PRIVATE_TUTORING])
            print(course.title)
        return course.theory_hours==course_hours[LType.THEORY] and course.lab_hours==course_hours[LType.LABORATORY] and course.tutoring_hours==course_hours[LType.PRIVATE_TUTORING]

    def semester_validance(self):
        validation_counter=0
        for course in self.courses:
            validation=self.course_validance(course)
            if validation:
                validation_counter+=1
        return validation_counter==len(self.courses)

    def __eq__(self, o:str) -> bool:
        return self.id==o
    
    def get_lock_timezones(self,zone,day):
        periods=zone.split('-')
        sh=int(periods[0].split(':')[0])
        eh=int(periods[1].split(':')[0])
        for timezone in Semester.timezones:
            zone_to_time=timezone.split("-")
            start_zone_time=int(zone_to_time[0].split(":")[0])
            end_zone_time=int(zone_to_time[1].split(":")[0])
            if start_zone_time>=sh and end_zone_time<=eh:
                self.locked_timezones[day].add(timezone) 

    def compute_program_penalty(self):
        semester_penalty=0
        return semester_penalty
        
    def export_semester_locked_timezones(self):
        workbook_path=os.path.join("","Schedule_Xlsx","marker_"+self.id+".xlsx")
        wb_obj=xlsxwriter.Workbook(workbook_path)
        ws_obj=wb_obj.add_worksheet()
        row=0
        column=1
        for day in Semester.days:
            cell_format=wb_obj.add_format()
            cell_format.set_bold()
            ws_obj.write(row,column,day,cell_format)
            column+=1
        row=1    
        column=0
        for timezone in Semester.timezones:
            cell_format=wb_obj.add_format()
            cell_format.set_bold()
            cell_format.set_rotation(10)
            ws_obj.write(row,column,timezone,cell_format)
            row+=1
        
        column=1
        for day in Semester.days:
            row=1
            for timezone in Semester.timezones:
                cell_format=wb_obj.add_format()
                cell_format.set_bg_color('red') if timezone in self.locked_timezones[day] else cell_format.set_bg_color('green')
                cell_format.set_bold()
                text="VALID" if timezone not in self.locked_timezones[day] else "INVALID"
                ws_obj.write(row,column,text,cell_format)
                row+=1
            column+=1
        wb_obj.close()
        print(termcolor.cprint(workbook_path,"green"))

    
        
