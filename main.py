from Source.problem import Timetable

def find_available_semesters(meetings):
    semesters=list()
    for meeting in meetings:
        if meeting.course.get_semester() not in semesters:
            semesters.append(meeting.course.get_semester())
    return semesters

def select_by_semester(meetings):
    print("Available semesters")
    available_semesters=find_available_semesters(meetings)
    for index,semester in enumerate(available_semesters):
        print('{}.Semester {}'.format(index+1,semester))
    y=int(input("Select Semester:"))
    return available_semesters[y-1]

def main():
    p=Timetable("DIT CBT")
    p.import_full_dit_schedule()
    semester=select_by_semester(p.meetings)
    p.print_semester_program(semester)

def store_schedule_scenario():
    p=Timetable("DIT CBT")
    p.import_full_dit_schedule()
    semesters=find_available_semesters(p.meetings)
    for semester in semesters:
        p.export_semester_program(semester)

def semester_validation():
    p=Timetable("DIT CBT")
    p.import_full_dit_schedule()
    p.validate_lessons_per_semester()

def semester_markers():
    p=Timetable("DIT CBT")
    p.import_full_dit_schedule()
    for semester in p.semester_info:
        semester.lock_timezones()
        print(semester.locked_timezones)
        semester.export_semester_locked_timezones()

if __name__=='__main__':
    semester_validation()
    # semester_markers()