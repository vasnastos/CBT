#include "core.hpp"
#include <iostream>
#include <vector>
#include <map>
#include <sstream>
#include <fstream>
#include <algorithm>
#include "graph.hpp"

class Problem
{
    private:
        std::string id;
        std::vector <Course> courses;
        std::vector <Lecturer> lecturers;
        std::vector <Room> rooms;
        std::map <std::string,std::vector <int>> curriculas;
        int days,periods_per_day,semesters;
        void course_lecturer_correspondence(const std::string course_name,const std::string &lecturer_name,bool is_tutoring=false);
        void course_lecturer_correspondence(const Course &course,const std::string &lecturer,bool is_tutoring=false);
        void course_lecture_correspondence(const std::string &course_name,const int &lecture_id,const std::string &lecturer);
    
    public:
        std::vector <Event> events;
        Graph G;

        Problem();
        void reset();
        void read_instance(std::string dataset_name);
        void create_events();
        void create_graph();
        
        // TODO
        int number_of_courses()const;
        int number_of_rooms()const;
        int number_of_curricula()const;
        int number_of_lecturers()const;
        int number_of_events()const;

        double conflict_density()const;
        double lecturers_availability()const;
        double room_suitability()const;
        friend std::ostream &operator<<(std::ostream &os,const Problem &problem);
};