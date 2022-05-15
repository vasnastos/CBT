#include <iostream>
#include <vector>
#include "course.hpp"
#include "classroom.hpp"


class Meeting
{
    private:
        std::string id;
        Course course;
        std::string curricula_id;
        int day;
        int period;
        std::vector <std::string> room_constraints;
        std::vector <std::pair <int,int>> period_constraints;
    
    public:
        Meeting(std::string mid);
        Meeting(std::string mid,const Course &c);
        void set_period(int d,int p);
        void set_curricula(std::string cid);
        void set_course(const Course &c);
        void add_constraint(int day,int period);
        void add_constraint(std::string room_id);
       

        std::string get_course_id()const;
        std::string get_id()const;
        std::string get_curricula()const;


        bool curricula_equality(const Meeting &m);
        bool course_equality(const Meeting &m);
        bool lecturer_equality(const Meeting &m);

        bool operator==(const Meeting &c)const;
        operator std::string()const;

        bool is_period_valid(std::pair <int,int> &p);
        bool is_room_valid(const Classroom &cr);
};