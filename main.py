from Source.problem import Problem

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
    p=Problem("DIT CBT")
    p.import_full_dit_schedule()
    semester=select_by_semester(p.meetings)
    p.print_semester_program(semester)

if __name__=='__main__':
    main()