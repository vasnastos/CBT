#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <filesystem>


class Course
{
    private:
        std::string course_id;
        std::string lecturer_id;
        int lecturer;
        int periods_to_take_place;
        int students;
        int building_id;
        int lecture_id;
        std::string curricula_id;
    public:
        Course(std::string cid,std::string lid,int lecturer_identification,int period_distro,int number_of_students,int bid,int lecid,int curid);
        ~Course();
        void set_lecturer(int lecturer_id);
        int get_lecturer_id();
        operator std::string()const;
};

class Classroom
{
    private:
        std::string room_id;
        int capacity;
        int building_id;
    public:
        Classroom(std::string rid,int capacity_place,int bid);
        ~Classroom();
        operator std::string()const;
};

class Curricula
{
    private:
        std::string curricula_id;
        std::vector <Course> courses;
        int S;
    public:
        Curricula(std::string cid);
        void add_course(const Course &c);
        bool is_curricula_of(std::string course_id);
        operator std::string()const;
};

class Lecturer
{
    private:
        std::string id;
        std::vector <Course> courses;
    public:
        Lecturer(std::string lecturer_id);
        void add_course(const Course &c);
        operator std::string()const;
};

class Meeting
{
    private:
        std::string id;
        std::string course;
        Lecturer lecturer;
        Curricula curricula;
        int day;
        int period;
    public:
        Meeting(std::string mid,std::string cid);
        void set_period(int d,int p);
        void add_constraint();
};

class Problem
{
    private:
        std::vector <Course> courses;        
};