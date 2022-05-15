#include <iostream>
#include <vector>
#include "course.hpp"

class Curricula
{
    private:
        std::string id;
        std::vector <Course> courses;
    public:
        Curricula(std::string cid);
        void add_course(const Course &c);
        bool find(std::string course_id);
        std::string get_id()const;
        int ncourses()const;
        operator std::string()const;
};