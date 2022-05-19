#include "department.hpp"

Course::Course(std::string cid,std::string tid,int nlectures,int distroperiods,int nstudents,int bid):id(cid),lecturer(tid),number_of_lectures(nlectures),max_periods_to_be_distributed(distroperiods),students(nstudents),building_id(bid) {}

Course::Course() {}

Course Course::operator=(const Course &c)
{
    this->id=c.id;
    this->number_of_lectures=c.number_of_lectures;
    this->students=c.students;
    this->lecturer=c.lecturer;
    this->unavailability_constraints=c.unavailability_constraints;
    this->room_constraints=c.room_constraints;
    this->building_id=c.building_id;
    this->curricula_id=c.curricula_id;
    this->max_periods_to_be_distributed=c.max_periods_to_be_distributed;
    return *this;
}

bool Course::operator==(const Course &c)const{
    return this->id==c.id;
}

void Course::add_constraint(int day,int period)
{
    this->unavailability_constraints.emplace_back(std::make_pair(day,period));
}

void Course::add_constraint(std::string room_id)
{
    this->room_constraints.emplace_back(room_id);
}

void Course::set_curricula(const std::string &cid)
{
    this->curricula_id=cid;
}

std::string Course::get_curricula()const
{
    return this->curricula_id;
}

std::string Course::get_id()const
{
    return this->id;
}

std::string Course::get_lecturer()const
{
    return this->lecturer;
}

int Course::get_number_of_lectures()const
{
    return this->number_of_lectures;
}

int Course::get_students()const
{
    return this->students;
}

bool Course::is_period_constraint(const int &day,const int &period)const
{
    return std::find_if(this->unavailability_constraints.begin(),this->unavailability_constraints.end(),[&](const std::pair <int,int> &p) {return p.first==day && p.second==period;})!=this->unavailability_constraints.end();
}

bool Course::is_room_constraint(const std::string &room_id)const
{
    return std::find(this->room_constraints.begin(),this->room_constraints.end(),room_id)!=this->room_constraints.end();
}

int Course::valid_periods(int days,int ppd)
{
    int vcounter=0;
    for(int i=0;i<days;i++)
    {
        for(int j=0;j<ppd;j++)
        {
            if(!this->is_period_constraint(i,j))
            {
                vcounter++;
            }
        }
    }
    return vcounter;
}
int Course::valid_rooms(std::vector <Room> &rooms)
{
    int vcounter=0;
    for(auto &room:rooms)
    {
        if(!this->is_room_constraint(room.get_id()))
        {
            vcounter++;
        }
    } 
    return vcounter;
}

std::ostream &operator<<(std::ostream &os,const Course &c)
{
    return os<<c.id<<"  RC:"<<c.room_constraints.size()<<"  UC:"<<c.unavailability_constraints.size()<<std::endl;
}

Room::Room(std::string rid,int cap,int bid):id(rid),capacity(cap),building_id(bid) {}

std::string Room::get_id()const
{
    return this->id;
}

int Room::get_capacity()const
{
    return this->capacity;
}

Curricula::Curricula(std::string &cid):id(cid) {}

std::string Curricula::get_id()const
{
    return this->id;
}

std::vector <Course> Curricula::get_courses()const
{
    return this->courses;
}

void Curricula::add_course(const Course &c)
{
    this->courses.emplace_back(c);
}

int Curricula::number_of_courses()const
{
    return this->courses.size();
}

int Curricula::number_of_lectures()const
{
    return std::accumulate(this->courses.begin(),this->courses.end(),0,[&](int s,const Course &c) {return s+c.get_number_of_lectures();});
}

Lecture::Lecture(const std::string &lid,const Course &cc):id(lid),course(cc) {}

std::string Lecture::get_id()const
{
    return this->id;
}

bool Lecture::course_equality(const Lecture &lec)
{
    return this->course==lec.course;
}
bool Lecture::teacher_equality(const Lecture &lec)
{
    return this->course.get_lecturer()==lec.course.get_lecturer();
}
bool Lecture::curricula_equality(const Lecture &lec)
{
    return this->course.get_curricula()==lec.course.get_curricula();
}

bool Lecture::operator==(const Lecture &lec)const
{
    return this->id==lec.id;
}

int Lecture::valid_periods(int days,int periods_per_day)const
{
    int vcounter=0;
    for(int i=0;i<days;i++)
    {
        for(int j=0;j<periods_per_day;j++)
        {
            if(!this->course.is_period_constraint(i,j))
            {
                vcounter++;
            }
        }
    }
    return vcounter;
}

int Lecture::valid_rooms(std::vector <Room> &rooms)const
{
    int vcounter=0;
    for(auto &x:rooms)
    {
        if(!this->course.is_room_constraint(x.get_id()))
        {
            vcounter++;
        }
    }
    return vcounter;
}