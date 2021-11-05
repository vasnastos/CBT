from Source.problem import Timetable

p=Timetable("DIT CBT")
p.import_full_dit_schedule()

def find_available_semesters():
    semesters=list()
    for meeting in p.meetings:
        if meeting.course.get_semester() not in semesters:
            semesters.append(meeting.course.get_semester())
    return semesters

def select_by_semester():
    print("Available semesters")
    available_semesters=find_available_semesters()
    for index,semester in enumerate(available_semesters):
        print('{}.Semester {}'.format(index+1,semester))
    y=int(input("Select Semester:"))
    return available_semesters[y-1]

def menu():
    choices=[
        "Show program per semester",
        "Show lecturer program",
        "validate program per semester"
    ]
    for index,choice in enumerate(choices):
        print(f"{index+1}.{choice}")
    y=int(input("Select an option:"))
    if y==1:
        semester=select_by_semester()
        p.print_semester_program(semester)
    elif y==2:
        lecturer_name="ΓΚΟΓΚΟΣ"
        p.export_program_by_lecturer(lecturer_name)
    else:
        p.validate_lessons_per_semester()
