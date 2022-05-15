#include "meeting.hpp"

Meeting::Meeting(std::string mid):id(mid),day(-1),period(-1) {}

Meeting::Meeting(std::string mid,const Course &c):id(mid),course(c) {}

void Meeting::set_period(int d,int p) 
{
    this->day=d;
    this->period=p;
}

void Meeting::set_curricula(std::string cid)
{
    this->curricula_id=cid;
}

void Meeting::add_constraint(int day,int period)
{
    this->period_constraints.emplace_back(std::make_pair(day,period));
}

void Meeting::add_constraint(std::string room_id)
{
    this->room_constraints.emplace_back(room_id);
}

std::string Meeting::get_course_id()const
{
    return this->course;
}

std::string Meeting::get_id()const
{
    return this->id;
}

bool Meeting::curricula_equality(const Meeting &m)
{
    return this->get_curricula()==m.get_curricula();
}

bool Meeting::course_equality(const Meeting &m)
{
    return this->course==m.course;
}
bool Meeting::lecturer_equality(const Meeting &m)
{
    return this->course.get_lecturer()==m.course.get_lecturer();
}

bool Meeting::operator==(const Meeting &c)const
{
    return this->id==c.id;
}

Meeting::operator std::string()const
{
    std::stringstream ss;
    ss<<"Meeting id:"<<this->id<<std::endl;
    ss<<"Course:"<<this->course.get_id()<<std::endl;
    ss<<"Curricula id:"<<this->curricula_id<<std::endl;
    ss<<"Day:"<<this->day<<std::endl;
    ss<<"Period:"<<this->period<<std::endl;
    ss<<"==== Period Constraint ===="<<std::endl;
    for(auto &rconstraint:this->room_constraints)
    {
        ss<<rconstraint<<std::endl;
    }
    ss<<std::endl<<std::endl;
    ss<<"==== Period Constraint ===="<<std::endl;
    for(auto &pconstraint:this->period_constraints)
    {
        ss<<""<<pconstraint.first<<","<<pconstraint.second<<")"<<std::endl;
    }
    ss<<std::endl<<std::endl;
}

std::string Meeting::get_curricula()const {
    return this->curricula_id;
}

bool Meeting::is_period_valid(std::pair <int,int> &p)
{
    for(auto &period_constraint:this->period_constraints)
    {
        if(period_constraint==p)
        {
            return false;
        }
    }
    return true;
}

bool Meeting::is_room_valid(const Classroom &cr)
{
    for(auto &room_constraint:this->room_constraints)
    {
        if(cr.get_id()==room_constraint)
        {
            return false;
        }
    }
    return true;
}