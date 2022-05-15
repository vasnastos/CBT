#include <iostream>
#include <vector>
#include "course.hpp"

class Lecturer
{
    private:
        std::string id;
        std::vector <Course> courses;
    public:
        Lecturer(std::string lecturer_id);
        std::string get_id()const;
        void add_course(const Course &c);
        operator std::string()const;
};