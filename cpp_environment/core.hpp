#include <string>
#include <vector>
#include <memory>
#include <tuple>
#include <sstream>
#include <filesystem>
namespace fs=std::filesystem;

enum class TYPE
{
    THEORY,
    LABORATORY,
    TUTORING
};

// ΛΟΓΙΣΜΙΚΟΥ, P1_X1,P1_X2,Ρ1_X3,Ρ1_Χ4,Ρ1_E1,Ρ1_Ε2,Ρ1_Ε3 
// ΕΥΦΥΗ ΣΥΣΤΗΜΑΤΑ ΚΑΙ ΕΦΑΡΜΟΓΕΣ,P2_X5,P2_X6,P2_X7,Ρ2_Ε4,Ρ2_Ε5
// YΠΟΛΟΓΙΣΤΙΚΑ ΣΥΣΤΗΜΑΤΑ,P3_X8,P3_X9,P3_X10,P3_E6,P3_E7,P3_E8
// ΤΗΛΕΠΙΚΟΙΝΩΝΙΕΣ,P4_X11,P4_X12,P4_X13,P4_E9,P4_E10
// ΔΙΚΤΥΑ,P5_X14, P5_X15,P5_X16,P5_E11,P5_E12,P5_13

enum class CURR
{
    SEMESTER,
    SOFTWARE,
    AI,
    COMPUTATIONAL_SYSTEMS,
    TELECOMMUNICATIONS,
    NETWORKING
};

class Room
{
    std::string id;
    std::string type;
    int capacity;
    public:
        Room(std::string room_id,std::string room_type,int room_capacity);
        ~Room();

        std::string get_id()const;
        std::string get_type()const;
        int get_capacity()const;
};

class Course
{
    std::string id;
    std::string name;
    int semester;
    int theory_hours;
    int lab_hours;
    int tutoring_hours;
    int credits;
    int lab_hours_in_use;
    CURR curricula_type;
    public:
        Course(std::string course_id,std::string course_name,int course_semester,int course_theory_hours,int course_tutoring_hours,int course_lab_hours,int course_credits);
        ~Course();

        void add_lab_used_hour(int number_of_hours);
        int get_lab_hours_used()const;
        void set_curricula_type(const CURR &curricula_type);

        std::string get_id()const;
        std::string get_name()const;
        int get_semester()const;
        int get_theory_hours()const;
        int get_tutoring_hours()const;
        int get_lab_hours()const;
        int get_credits()const;
        CURR get_curricula()const;

        int begin_theory()const;
        int end_theory()const;
        int begin_tutoring()const;
        int end_tutoring()const;
        int begin_lab()const;
        int end_lab()const;
        int get_lab_hours_in_use()const;

        bool operator==(const Course &course)const;
};

class Lecturer
{
    private:
        std::string name;
        std::string email;
        std::string username;

    public:
        std::vector <int> events;

        Lecturer(std::string lecturer_name,std::string lecturer_email,std::string lecturer_username);
        ~Lecturer();

        void set_name(std::string name);
        void set_email(std::string email);
        void set_username(std::string username);

        std::string get_name()const;
        std::string get_email()const;
        std::string get_usename()const;
        
        void add_event(const int &event_id);     
};

class Event
{
    Course *course;
    Lecturer *lecturer;
    int lecture_id;
    TYPE type; // th,l,tut
    public:
        Event(Course *course_obj,int lid,TYPE t);
        ~Event();

        void setLecturer(Lecturer &newlecturer);
        bool same_curricula(const Event &e);
        std::string get_type_str()const;
        int get_lecture_id()const;
        TYPE get_type()const;
        operator std::string()const;
        bool is_events_course(const Course &ecourse)const;
};

CURR get_curricula_type(const std::string &curr_type);
TYPE get_course_type(const std::string &course_type);