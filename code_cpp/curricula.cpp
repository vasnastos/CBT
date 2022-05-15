#include "curricula.hpp"

Curricula::Curricula(std::string cid):id(cid) {}

void Curricula::add_course(const Course &c) {this->courses.emplace_back(c);}

bool Curricula::find(std::string course_id)
{
    return std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==course_id;})!=this->courses.end();
}

std::string Curricula::get_id()const
{
    return this->id;
}

int Curricula::ncourses()const {return this->courses.size();}

Curricula::operator std::string()const
{
    std::stringstream ss;
    ss<<"Curricula Id:"<<this->id<<std::endl;
    ss<<"Courses:[";
    for(int i=0,t=this->courses.size();i<t;i++)
    {
        if(i==t-1)
        {
            ss<<this->courses.at(i).get_id()<<"]";
            continue;
        }
        ss<<this->courses.at(i).get_id()<<",";
    }
    ss<<"=>"<<this->courses.size();
    return ss.str();
}