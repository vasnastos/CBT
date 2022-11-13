#include "core.hpp"
#include <iostream>
#include <vector>
#include <map>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <windows.h>
#include "graph.hpp"


class Problem
{
    private:
        std::string id;
        std::vector <Course> courses;
        std::vector <Lecturer> lecturers;
        std::vector <Room> rooms;
        std::map <std::string,std::vector <std::string>> curriculas;
        std::map <std::string,std::vector <std::tuple<std::string,int,std::string>>> assignments;
        int days,periods_per_day,semesters;
        void course_lecturer_correspondence(const std::string &course_name,const std::string &lecturer_name,const int &number_of_lectures,const std::string &type_of_lecture);
        void events_assignment();
        
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

        static void change_problem_path(const std:: vector <std::string> &files);
        static std::string path_to_datasets;
};