#include "course.hpp"

Course::Course(std::string cid,std::string lid,int number_of_meetings,int period_distro,int number_of_students,int bid):id(cid),lecturer(lid),lectures(number_of_meetings),building_id(bid),lecture_id(1) {}

Course::Course():id(""),lecturer(""),lectures(-1),periods_to_take_place(-1),students(-1),building_id(-1),lecture_id(1) {}

Course::~Course() {}

void Course::set_lecturer(const std::string &vlecturer)
{
    this->lecturer=vlecturer;
}

std::string Course::get_lecturer()const
{
    return this->lecturer;
}

int Course::get_lecture_current_id()
{
    return this->lecture_id++;
}

std::string Course::get_id()const
{
    return this->id;
}

Course::operator std::string()const
{
    std::stringstream ss;
    ss<<"Course id:"<<this->id<<std::endl;
    ss<<"Course Lecturer:"<<this->lecturer<<std::endl;
    ss<<"Course Meetings:"<<this->lectures<<std::endl;
    ss<<"Course Students:"<<this->students<<std::endl;
    ss<<"Course Periods spread:"<<this->periods_to_take_place<<std::endl;
    ss<<"Course building id:"<<this->building_id<<std::endl;
    ss<<"Course curricula id:"<<this->curricula_id<<std::endl;
    return ss.str();
}

bool Course::operator==(const Course &c)const
{
    return this->id==c.id;
}

Course &Course::operator=(const Course &c)
{
    this->id=c.id;
    this->lecture_id=c.lecture_id;
    this->curricula_id=c.curricula_id;
    this->building_id=c.building_id;
    this->lectures=c.lectures;
    this->lecturer=c.lecturer;
    this->periods_to_take_place=c.periods_to_take_place;
    this->students=c.students;
    return *this;
}

std::string Course::get_lecturer()const
{
    return this->lecturer;
}