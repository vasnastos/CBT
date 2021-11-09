import helper
from Source.database import database
from Source.problem import Timetable

def database_import():
    db=database('cbt_base.db')
    db.create_tables()
    prob=Timetable("Dit Uoi")
    prob.import_full_dit_schedule()
    for course in prob.courses:
        db.insert_course(course.id,course.title,course.semester,course.flow,course.theory_hours,course.lab_hours,course.tutoring_hours,course.credits)
    for classroom in prob.classrooms:
        db.insert_classsroom(classroom.id,classroom.type,classroom.capacity)
    for lecturer in prob.lecturers:
        db.insert_lecturer(lecturer.name,lecturer.rank.value,lecturer.mail,lecturer.identifier)
    for lecture in prob.lectures:
        print(lecture.ltype.value,lecture.duration,lecture.classroom.id,lecture.lecturer.identifier,lecture.course.id)
        db.insert_lecture(lecture.ltype.value,lecture.duration,lecture.classroom.id,lecture.lecturer.identifier,lecture.course.id)
    for meeting in prob.meetings:
        db.insert_meeting(meeting.start_hour,meeting.end_hour,meeting.day,meeting.get_class_id(),meeting.get_lecturer_id(),meeting.get_course_id(),meeting.get_semester())

def database_save():
    db=database('cbt_base.db')
    prob=Timetable('Dit_Uoi')
    prob.import_full_dit_schedule()
    db.courses_to_txt()

if __name__=='__main__':
    # helper.menu()
    # database_import()
    database_save()
    