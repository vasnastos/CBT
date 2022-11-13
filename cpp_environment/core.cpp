#include "core.hpp"

Course::Course(std::string course_id,std::string course_name,int course_semester,int course_theory_hours,int course_tutoring_hours,int course_lab_hours,int course_credits):id(course_id),name(course_name),semester(course_semester),theory_hours(course_theory_hours),tutoring_hours(course_tutoring_hours),credits(course_credits),lab_hours_in_use(0) {}
Course::~Course() {}

std::string Course::get_id()const {return this->id;}
std::string Course::get_name()const {return this->name;}
int Course::get_theory_hours()const {return this->theory_hours;}
int Course::get_tutoring_hours()const {return this->tutoring_hours;}
int Course::get_semester()const {return this->semester;}
int Course::get_lab_hours()const {return this->lab_hours;}
int Course::get_credits()const {return this->credits;}
int Course::begin_theory()const {return 0;}
int Course::end_theory()const {return this->theory_hours;}
int Course::begin_tutoring()const {return this->theory_hours;}
int Course::end_tutoring()const {return this->theory_hours+this->tutoring_hours;}
int Course::begin_lab()const {return this->theory_hours+this->tutoring_hours;}
int Course::end_lab()const {return this->theory_hours+this->tutoring_hours+this->lab_hours;}
bool Course::operator==(const Course &course)const {return this->id==course.id;}
void Course::add_lab_used_hour(int number_of_hours) {this->lab_hours_in_use+=number_of_hours;}
void Course::set_curricula_type(const CURR &curricula_type) {this->curricula_type=curricula_type;}
int Course::get_lab_hours_in_use()const {return  this->lab_hours_in_use;}
int Course::get_lab_hours_used()const {return this->lab_hours_in_use;}
CURR Course::get_curricula()const {return this->curricula_type;}

Room::Room(std::string room_id,std::string room_type,int room_capacity):id(room_id),type(room_type),capacity(room_capacity) {}
Room::~Room() {}

std::string Room::get_id()const {return this->id;}
std::string Room::get_type()const {return this->type;}
int Room::get_capacity()const {return this->capacity;}

Lecturer::Lecturer(std::string lecturer_name,std::string lecturer_email,std::string lecturer_username):name(lecturer_name),email(lecturer_email),username(lecturer_username) {}
Lecturer::~Lecturer() {}
void Lecturer::set_name(std::string name) {this->name=name;}
void Lecturer::set_email(std::string email) {this->email=email;}
void Lecturer::set_username(std::string username) {this->username=username;}
std::string Lecturer::get_name()const {return this->name;}
std::string Lecturer::get_email()const {return this->email;}
std::string Lecturer::get_usename()const {return this->username;}   
void Lecturer::add_event(const int &event_id) {this->events.emplace_back(event_id);}


Event::Event(Course *course_obj,int lid,TYPE t):course(course_obj),lecture_id(lid),type(t) {}
Event::~Event() {}
std::string Event::get_type_str()const
{
    switch (this->type)
    {
    case TYPE::THEORY:
        return "Theory";
        break;
    case TYPE::LABORATORY:
        return "Laboratory";
        break;
    case TYPE::TUTORING:
        return "Tutoring";
        break;
    default:
        return "";
        break;
    }
}

TYPE Event::get_type()const 
{
    return this->type;
}

Event::operator std::string()const
{
    std::stringstream ss;
    ss<<this->course->get_name()<<"("<<this->get_type_str()<<") "<<this->lecturer->get_name();
    return ss.str();
}

bool Event::same_curricula(const Event &e)
{
    if(this->course->get_semester()==e.course->get_semester())
    {
        if(this->course->get_semester()>=7)
        {
            return int(this->course->get_curricula())==int(e.course->get_curricula());
        }
        else
        return true;
    }
    return false;
}

void Event::setLecturer(Lecturer &newlecturer)
{
    this->lecturer=&newlecturer;
}

bool Event::is_events_course(const Course &ecourse)const
{
    return *this->course==ecourse;
}

int Event::get_lecture_id()const
{
    return this->lecture_id;
}

TYPE get_course_type(const std::string &course_type)
{
    // th,tut,l
    if(course_type=="th")
    {
        return TYPE::THEORY;
    }
    else if(course_type=="tut")
    {
        return TYPE::TUTORING;
    }
    else
    {
        return TYPE::LABORATORY;
    }
}

CURR get_curricula_type(const std::string &curr_type)
{
    if(curr_type=="ΛΟΓΙΣΜΙΚΟ")
    {
        return CURR::SOFTWARE;
    }
    else if(curr_type=="ΕΥΦΥΗ ΣΥΣΤΗΜΑΤΑ ΚΑΙ ΕΦΑΡΜΟΓΕΣ")
    {
        return CURR::AI;
    }
    else if(curr_type=="YΠΟΛΟΓΙΣΤΙΚΑ ΣΥΣΤΗΜΑΤΑ")
    {
        return CURR::COMPUTATIONAL_SYSTEMS;
    }
    else if(curr_type=="ΤΗΛΕΠΙΚΟΙΝΩΝΙΕΣ")
    {
        return CURR::TELECOMMUNICATIONS;
    }
    else if(curr_type=="ΔΙΚΤΥΑ")
    {
        return CURR::NETWORKING;
    }
    else
    {
        return CURR::SEMESTER;
    }
}

