#include <iostream>
#include <vector>
#include <map>
#include <typeinfo>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <algorithm>
#include <numeric>
#include <cmath>
#include "course.hpp"
#include "classroom.hpp"
#include "lecturer.hpp"
#include "curricula.hpp"
#include "meeting.hpp"

namespace fs=std::filesystem;

// Graph represantation
class Graph
{
    private:
        std::map <std::string,std::vector <std::string>> adj_matrix;
    public:
        std::vector <std::string> nodes;
        std::vector <std::pair <std::string,std::string>> edges;
        Graph();
        void add_node(const std::string &lecture);
        void add_edge(const std::string &l1,const std::string &l2);
        bool has_edge(const std::string &l1,const std::string &l2);
        friend std::ostream &operator<<(std::ostream &os,const Graph &g);
};

class Problem
{
    private:
        std::string id;
        std::vector <Course> courses;
        std::vector <Lecturer> lecturers;
        std::vector <Meeting> meetings;
        std::vector <Classroom> classrooms;
        std::vector <Curricula> curriculas;
        std::vector <std::pair<int,int>> aperiods;
        Graph G;
        int M; //Number of meetings
        int P;  // Number of periods
        int C;  // Number of courses
        int LC; // Number of lecturers
        int R;  // Number of classrooms
        int CR; // Number of curricula
        int min_lecturers_in_day;
        int max_lecturers_in_day;
        int days;
        int periodspd; // periods per day

    public:
        static std::string datasets_root;
        static void set_path_to_dataset(const std::string &path_to_ds);
        static void set_path_to_dataset();

        Problem();
        Problem(std::string pid);
        void load_udine();
        double conflict_density();
        double teachers_availability();
        double room_suitability();
        int curricula_index(std::string course_id);
        int lectures_per_day_rate();
        int room_occupation();
        void create_graph();
        std::vector <std::string> find_neighbors(const Meeting &m);
};

class Solution
{
    private:

};