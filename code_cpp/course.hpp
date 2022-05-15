#include <iostream>
#include <sstream>
#include <string>

class Course
{
    private:
        std::string id;
        std::string lecturer;
        int lectures;
        int lecture_id;
        int periods_to_take_place;
        int students;
        int building_id;
        std::string lecturer;
        std::string curricula_id;
    
    public:
        Course();
        Course(std::string cid,std::string lid,int number_of_meetings,int period_distro,int number_of_students,int bid);
        ~Course();

        operator std::string()const;
        Course &operator=(const Course &c);
        bool operator==(const Course &c)const;

        void set_lecturer(const std::string &vlecturer);

        std::string get_id()const;
        std::string get_lecturer()const;
        std::string get_curricula_id()const;
        int get_lecture_current_id();
};