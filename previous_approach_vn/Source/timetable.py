from Source.constant_vars import Constant
from Source.database import Cbt_database
from termcolor import cprint
from prettytable import PrettyTable
from prettytable import ALL

from Source.semester import Semester
from Source.database import Cbt_database

class Timetable:
    def __init__(self):
        self.db=Cbt_database('cbt_base.db')
        self.meetings=self.db.meetings()
        self.lecturers=self.db.lecturers()
        self.lectures=self.db.lectures()
        self.courses=self.db.courses()
        self.info_per_semester=list()
        self.create_schema()


    def add_meeting_per_lecturer(self):
        for lecturer in self.lecturers:
            lecturer_meetings=self.db.get_meetings_by_lecturer(lecturer.identifier)
            lecturer.set_lecturer_meetings(lecturer_meetings)
    
    def add_semester_info(self):
        for meeting in self.meetings:
            if meeting.get_semester() in self.info_per_semester:
                continue
            self.info_per_semester.append(Semester(meeting.get_semester()))

        for semester in self.info_per_semester:
            if "-" in semester.id:
                semester_id=semester.id.split('-')
                course_semester=int(semester_id[0])
                course_flow=semester_id[1]
                for course in self.courses:
                    if course.semester==course_semester and course.flow==course_flow:
                        semester.add_course(course)
    
    def add_meeting_info_per_semester(self):
        for meeting in self.meetings:
            self.info_per_semester[self.info_per_semester.index(meeting.course.get_semester())].add_meeting(meeting)

    def create_schema(self):
        self.add_meeting_per_lecturer()
        self.add_semester_info()
        self.add_meeting_info_per_semester()


    def add_lecturer_validation_exceptions(self,identifier):
        pass
    
    def lecturer_validation(self):
        for lecturer in self.lecturers:
            validate_lecturer=lecturer.lecturer_validation()
            print(validate_lecturer)
            if validate_lecturer:
                cprint(str(lecturer),'green')
            else:
                cprint(str(lecturer),'red')
            print('\n\n')

    def print_semester_program(self):
        available_semester=[semester.id for semester in self.info_per_semester]
        for index,value in enumerate(available_semester):
            print(f'{index+1}.{value}')
        semester=available_semester[int(input('Select semester:'))-1]
        table=PrettyTable()
        table.hrules=ALL
        namefield=[' ']
        namefield.extend(Constant.days)
        table.field_names=namefield
        widths={name:30 for name in namefield}
        table._max_width=widths
        for timestamp in Constant.timezones:
            row=list()
            start_time=int(timestamp.split('-')[0].split(':')[0])
            end_time=int(timestamp.split('-')[1].split(':')[0])
            row.append(timestamp)
            for day in Constant.days:
                meeting_schedule=str()
                for meeting in self.info_per_semester[self.info_per_semester.index(semester)].meetings[day]:
                        meeting_start_time=int(meeting.start_hour.split(":")[0])
                        meeting_end_time=int(meeting.end_hour.split(":")[0])
                        if meeting_start_time<=start_time and meeting_end_time>=end_time:
                            meeting_schedule+=meeting.description()+"\n"
                row.append(meeting_schedule)
            table.add_row(row)
        print(table)
    
    def print_all(self):
        print(len(self.lectures))
        print(len(self.lecturers))
        print(len(self.courses))
        print(len(self.meetings))

    def timetable_cost(self):
        pass
