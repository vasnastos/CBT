#include "department.hpp"
#include <filesystem>
#include <fstream>
#include <numeric>
#include <set>
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
        

    public:
        static std::vector <std::string> dataset_source;
        static void init_source();
        Problem(const std::string &dataset_name);
        void load_udine();

        double conflict_density(std::string per="course");
        double teachers_availability(std::string per="course");
        double room_suitability(std::string per="course");
        double room_occupation(std::string per="course");
        double lectures_per_day_per_curriculum();
        int total_seats();
        int total_students();
        int min_curriculum_lectures();
        int max_curriculum_lectures();

};