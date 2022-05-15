#include "classroom.hpp"

Classroom::Classroom(std::string rid,int capacity_place,int bid):id(rid),capacity(capacity_place),building_id(bid) {}

Classroom::~Classroom() {}

std::string Classroom::get_id()const
{
    return this->id;
}

Classroom::operator std::string()const
{
    std::stringstream ss;
    ss<<"Room id:"<<this->id<<std::endl;
    ss<<"Capacity:"<<this->capacity<<std::endl;
    ss<<"Building id:"<<this->building_id<<std::endl;
    return ss.str();
}