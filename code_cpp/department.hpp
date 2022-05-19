#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <cmath>

class Room
{
    private:
        std::string id;
        int capacity;
        int building_id;
    public:
        Room(std::string rid,int cap,int bid);
        std::string get_id()const;
        int get_capacity()const;
};


class Course
{
    private:
        std::string id;
        int number_of_lectures;
        int students;
        std::string lecturer;
        std::vector <std::pair<int,int>> unavailability_constraints;
        std::vector <std::string> room_constraints;
        int building_id;
        int max_periods_to_be_distributed;
        std::string curricula_id;

    public:
        Course(std::string cid,std::string tid,int nlectures,int distroperiods,int nstudents,int bid);
        Course();

        Course operator=(const Course &c);
        bool operator==(const Course &c)const;

        void add_constraint(int day,int period);
        void add_constraint(std::string room_id);
        void set_curricula(const std::string &cid);

        std::string get_curricula()const;
        std::string get_id()const;
        std::string get_lecturer()const;
        int get_students()const;
        int get_number_of_lectures()const;

        bool is_period_constraint(const int &day,const int &period)const;
        bool is_room_constraint(const std::string &room_id)const;

        int valid_periods(int days,int ppd);
        int valid_rooms(std::vector <Room> &rooms);
        friend std::ostream &operator<<(std::ostream &os,const Course &c);
};


class Curricula
{
    private:
        std::string id;
        std::vector <Course> courses;
    public:
        Curricula(std::string &cid);
        std::string get_id()const;
        std::vector <Course> get_courses()const;
        void add_course(const Course &c);
        int number_of_courses()const;
        int number_of_lectures()const;
};

class Lecture
{
    private:
        std::string id;
        Course course;
    public:
        Lecture(const std::string &lid,const Course &cc);
        std::string get_id()const;
        bool course_equality(const Lecture &lec);
        bool teacher_equality(const Lecture &lec);
        bool curricula_equality(const Lecture &lec);
        bool operator==(const Lecture &lec)const;

        int valid_periods(int days,int periods_per_day)const;
        int valid_rooms(std::vector <Room> &rooms)const;
};