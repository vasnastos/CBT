#include "problem.hpp"

Problem::Problem() {}

void Problem::reset()
{   
    this->courses.clear();
    this->curriculas.clear();
    this->rooms.clear();
    this->lecturers.clear();
}

void Problem::read_instance(std::string dataset_name)
{
    std::fstream fs;
    std::string line,word,category;
    fs.open(dataset_name,std::ios::in);
    if(!fs.is_open())
    {
        std::cerr<<"File:"<<dataset_name<<" did not open properly"<<std::endl;
        return;
    }
    int line_counter=0;
    std::map <std::string,std::string> configurations;
    std::vector <std::string> data;
    while(std::getline(fs,line))
    {
        if(line_counter<6)
        {   
            std::stringstream ss(line);
            data.clear();
            while(std::getline(ss,word,':'))
            {
                data.emplace_back(word);
            }
            configurations[data[0]]=data[1];
            line_counter++;
            continue;
        }
        // find course category
        if(line=="" || line.at(0)=='#')
        {
            continue;
        }

        if(line=="COURSES")
        {
            category="COURSES";
            continue;
        }
        else if(line=="LECTURERS")
        {
            category="LECTURES";
            continue;
        }
        else if(line=="CLASSROOMS")
        {
            category="CLASSROOMS";
            continue;
        }
        else if(line=="CURRICULA")
        {
            category="CURRICULA";
            continue;
        }

        std::stringstream ss(line);
        data.clear();       
        while(std::getline(ss,word,','))
        {
            data.emplace_back(word);
        }

        if(category=="COURSES")
        {
            this->courses.emplace_back(Course(data[0],data[1],std::stoi(data[2]),std::stoi(data[3]),std::stoi(data[4]),std::stoi(data[5]),std::stoi(data[6])));
            this->curriculas["semester_"+data[2]].emplace_back(this->courses.size()-1);
            if(this->courses[this->courses.size()-1].get_semester()<7)
            {
                this->courses[this->courses.size()-1].set_curricula_type(CURR::SEMESTER);
            }
        }
        else if(category=="CLASSROOMS")
        {
            this->rooms.emplace_back(Room(data[0],data[1],std::stoi(data[2])));
        }
        else if(category=="LECTURERS")
        {
            this->lecturers.emplace_back(Lecturer(data[0],data[1],data[2]));
        }
        else if(category=="ASSIGNMENTS")
        {
            // # lesson,lecturer,hours of each lab,number of labs
            if(data[4]=="th")
            {
                this->course_lecturer_correspondence(data[0],data[1]);
            }
            else if(data[4]=="l"){
                this->course_lecture_correspondence(data[0],std::stoi(data[3]),data[1]);
            }
        }
        else if(category=="CURRICULA")
        {
            std::string type=data[0];
            for(int i=1,t=data.size();i<t;i++)
            {
                std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==data[i];})->set_curricula_type(get_curricula_type(data[0]));
                this->curriculas[data[0]].emplace_back(data[i]);
            }
        }
    }
    this->create_events();
    
    this->semesters=std::stoi(configurations["semester"]);
    this->days=std::stoi(configurations["days"]);
    this->periods_per_day=std::stoi(configurations["periods"]);
}

void Problem::create_graph()
{
    for(int i=0,t=this->events.size();i<t;i++)
    {
        for(int j=i+1;j<t;j++)
        {
            if(this->events[i].same_curricula(this->events[j]))
            {
                if(this->events[i].get_type()==TYPE::THEORY && this->events[j].get_type()==TYPE::THEORY)
                {
                    this->G.add_edge(i,j);
                }
                else if((this->events[i].get_type()==TYPE::THEORY && this->events[j].get_type()==TYPE::LABORATORY) || (this->events[i].get_type()==TYPE::LABORATORY && this->events[j].get_type()==TYPE::THEORY))
                {
                    this->G.add_edge(i,j);
                }
            }
        }
    }
}

void Problem::course_lecturer_correspondence(const std::string course_name,const std::string &lecturer_name,bool is_tutoring=false)
{
    auto course=std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &vcourse) {return vcourse.get_name()==course_name;});
    auto lecturer=std::find_if(this->lecturers.begin(),this->lecturers.end(),[&](const Lecturer &lecturer) {return lecturer.get_name()==lecturer_name;});
    if(lecturer==this->lecturers.end() || course==this->courses.end()) return;
    int course_index=course-this->courses.begin();
    if(!is_tutoring)
    {
        for(int i=course->begin_theory();i<course->end_theory();i++)
        {
            lecturer->add_lecture(std::make_pair(course_index,i));
        }
    }
    else
    {
        for(int tut_i=course->begin_tutoring();tut_i<course->end_tutoring();tut_i++)
        {
            lecturer->add_lecture(std::make_pair(course_index,tut_i));
        }   
    }
}

void Problem::course_lecturer_correspondence(const Course &course,const std::string &lecturer_name,bool is_tutoring)
{
    auto lecturer=std::find_if(this->lecturers.begin(),this->lecturers.end(),[&](const Lecturer &lecturer) {return lecturer.get_name()==lecturer_name;});
    if(lecturer==this->lecturers.end()) return;
    int course_index=std::find(this->courses.begin(),this->courses.end(),course)-this->courses.begin();
    if(!is_tutoring)
    {
        for(int i=course.begin_theory();i<course.end_theory();i++)
        {
            
            lecturer->add_lecture(std::make_pair(course_index,i));
        }
    }
    else
    {
        for(int tut_i=course.begin_tutoring();tut_i<course.end_tutoring();tut_i++)
        {
            lecturer->add_lecture(std::make_pair(course_index,tut_i));
        }   
    }
}

void Problem::course_lecture_correspondence(const std::string &course_name,const int &lab_hours,const std::string &lecturer_name)
{
    auto course=std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &cr) {return cr.get_name()==course_name;});
    auto lecturer=std::find_if(this->lecturers.begin(),this->lecturers.end(),[&](const Lecturer &lecturer) {return lecturer.get_name()==lecturer_name;});
    if(lecturer==this->lecturers.end()) return;
    int course_index;
    for(int lab_i=course->begin_lab()+course->get_lab_hours_in_use();lab_i<+course->get_lab_hours_in_use()+course->begin_lab()+lab_hours;lab_i++)
    {
        course_index=std::find(this->courses.begin(),this->courses.end(),course)-this->courses.begin();
        lecturer->add_lecture(std::make_pair(course_index,lab_i));
    }
    course->add_lab_used_hour(lab_hours);
}

void Problem::create_events()
{
    for(auto &course:this->courses)
    {
        for(int lecture_i=course.begin_theory();lecture_i<course.end_theory();lecture_i++)
        {
            this->events.emplace_back(Event(&course,lecture_i,TYPE::THEORY));
        }
        for(int lecture_i=course.begin_tutoring();lecture_i<course.end_tutoring();lecture_i++)
        {
            this->events.emplace_back(Event(&course,lecture_i,TYPE::TUTORING));
        }
        for(int lecture_i=course.begin_lab();lecture_i<course.end_lab();lecture_i++)
        {
            this->events.emplace_back(Event(&course,lecture_i,TYPE::LABORATORY));
        }   
    }
}

int Problem::number_of_courses()const {return this->courses.size();}
int Problem::number_of_rooms()const {return this->rooms.size();}
int Problem::number_of_curricula()const {return this->curriculas.size();}
int Problem::number_of_lecturers()const {return this->lecturers.size();}
int Problem::number_of_events()const {return this->events.size();}

std::ostream &operator<<(std::ostream &os,const Problem &problem)
{
    //TODO
}


double Problem::conflict_density()const
{

}
double Problem::lecturers_availability()const
{

}
double Problem::room_suitability()const
{

}