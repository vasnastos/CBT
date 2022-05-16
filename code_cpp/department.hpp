#include <iostream>
#include <vector>

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
        int get_number_of_lectures()const;

        bool is_period_constraint(const int &day,const int &period)const;
        bool is_room_constraint(const std::string &room_id)const;

        int valid_periods(int days,int ppd);
        int valid_rooms(std::vector <Room> &rooms);
};


class Room
{
    private:
        std::string id;
        int capacity;
        int building_id;
    public:
        Room(std::string rid,int cap,int bid);
        std::string get_id()const;
};

class Curricula
{
    private:
        std::string id;
        std::vector <Course> courses;
    public:
        Curricula(std::string &cid);
        void add_course(const Course &c);
};

class Lecture
{
    private:
        std::string id;
        Course course;
    public:
        Lecture(const std::string &lid,const Course &cc);
        bool course_equality(const Lecture &lec);
        bool teacher_equality(const Lecture &lec);
        bool curricula_equality(const Lecture &lec);
        bool operator==(const Lecture &lec)const;

        int valid_periods(int days,int periods_per_day)const;
        int valid_rooms(std::vector <Room> &rooms)const;
};