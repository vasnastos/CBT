#include "department.hpp"
#include <filesystem>
#include <fstream>
<<<<<<< HEAD
#include <set>
#include <map>
=======
#include <numeric>
#include <set>
>>>>>>> 7276d56c3ee6ca88866a0e062440fab71aeb7bcd
#include <sstream>

// Structure of first nine lines
// Name: Ing0809-1
// Courses: 142
// Rooms: 21
// Days: 5
// Periods_per_day: 5
// Curricula: 83
// Min_Max_Daily_Lectures: 2 3
// UnavailabilityConstraints: 841
// RoomConstraints: 426

namespace fs=std::filesystem;

<<<<<<< HEAD
class Graph
{
    private:
        std::map <std::string,std::vector <std::string>> adj_list;
    public:
        Graph();
        std::vector <std::pair <std::string,std::string>> edges;
        std::vector <std::string> nodes;
        void add_node(const std::string &node);
        void add_edge(const std::string &e1,const std::string &e2);
        bool has_edge(const std::string &e1,const std::string &e2);
        friend std::ostream &operator<<(std::ostream &os,const Graph &g);
};


=======
>>>>>>> 7276d56c3ee6ca88866a0e062440fab71aeb7bcd
class Problem
{
    private:
        std::string id;
        std::set <std::string> lecturers;
        std::vector <Course> courses;
        std::vector <Room> rooms;
        std::vector <Curricula> curriculas;
        std::vector <std::tuple<std::string,int,int>> unavailability_constraints;
        std::vector <std::pair <std::string,std::string>> room_constraints;
        std::vector <Lecture> lectures;

        // Abbreviations
        int C;// number of courses
        int R;// number of rooms
        int CL;//number of curriculas
        int S;// number of students;
        int D;// total days
        int L;// number of lectures
        int PPD; // periods per day
        int MNDL;// Min daily lectures
        int MXDL;//Max Daily lectures
        int UNC; //number of unavailability constraints
        int RC;// number of room constraints
        int LCS; //number of lectures
        int P; // number of periods
        
<<<<<<< HEAD
        Graph G;

    public:
        static std::vector <std::string> dataset_source;
        static std::vector <std::string> dataset_names;
        static void init_source();
        static std::string path_to_datasets;
        Problem(const std::string &dataset_name);
        void load_udine();
        void create_graph();
=======

    public:
        static std::vector <std::string> dataset_source;
        static void init_source();
        Problem(const std::string &dataset_name);
        void load_udine();
>>>>>>> 7276d56c3ee6ca88866a0e062440fab71aeb7bcd

        double conflict_density(std::string per="course");
        double teachers_availability(std::string per="course");
        double room_suitability(std::string per="course");
<<<<<<< HEAD
        double room_occupation(std::string per="room");
        std::string lectures_per_day_per_curriculum();

=======
        double room_occupation(std::string per="course");
        double lectures_per_day_per_curriculum();
>>>>>>> 7276d56c3ee6ca88866a0e062440fab71aeb7bcd
        int total_seats();
        int total_students();
        int min_curriculum_lectures();
        int max_curriculum_lectures();

<<<<<<< HEAD
        void summary();
};
=======
};
>>>>>>> 7276d56c3ee6ca88866a0e062440fab71aeb7bcd
