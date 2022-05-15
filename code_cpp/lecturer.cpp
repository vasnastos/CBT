#include "lecturer.hpp"

Lecturer::Lecturer(std::string lecturer_id):id(lecturer_id) {}

void Lecturer::add_course(const Course &c)
{
    this->courses.emplace_back(c);
}

std::string Lecturer::get_id()const
{
    return this->id;
}

Lecturer::operator std::string()const
{
    std::stringstream ss;
}