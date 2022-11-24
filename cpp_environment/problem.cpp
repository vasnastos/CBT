#include "problem.hpp"
#include "string_handler.hpp"

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
    fs::path apath(".");
    for(const auto &x:{Problem::path_to_datasets,dataset_name})
    {
        apath.append(x);
    }

    std::fstream fs;
    std::string line,word,category;
    fs.open(apath.string(),std::ios::in);
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
        // std::cout<<"Line:"<<line<<std::endl;
        if(line_counter<6)
        {   
            std::stringstream ss(line);
            data.clear();
            while(std::getline(ss,word,':'))
            {
                data.emplace_back(trim(word));
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
            category="LECTURERS";
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
        else if(line=="ASSIGNMENTS")
        {
            category="ASSIGNMENTS";
            continue;
        }

        std::stringstream ss(line);
        data.clear();       
        while(std::getline(ss,word,','))
        {
            data.emplace_back(trim(word));
        }

        if(category=="COURSES")
        {
            data[1]=upper(data[1]);
            std::cout<<data[1]<<std::endl;
            this->courses.emplace_back(Course(data[0],data[1],std::stoi(data[2]),std::stoi(data[3]),std::stoi(data[4]),std::stoi(data[5]),std::stoi(data[6])));
            this->curriculas["semester_"+data[2]].emplace_back(data[1]);
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
            std::for_each(data[1].begin(),data[1].end(),[](char &c) {c=::toupper(c);});
            this->lecturers.emplace_back(Lecturer(data[0],data[1],data[2]));
        }
        else if(category=="ASSIGNMENTS")
        {
            // # lesson,lecturer,hours of each lab,number of labs
            data[0]=upper(data[0]);
            this->course_lecturer_correspondence(data[0],data[1],std::stoi(data[3]),data[4]);
        }
        else if(category=="CURRICULA")
        {
            for(int i=1,t=data.size();i<t;i++)
            {
                std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==data[i];})->set_curricula_type(get_curricula_type(data[0]));
                this->curriculas[data[0]].emplace_back(data[i]);
            }
        }
    }
    fs.close();

    this->create_events();
    this->events_assignment();
    
    this->semesters=std::stoi(configurations["semesters"]);
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

void Problem::course_lecturer_correspondence(const std::string &course_name,const std::string &lecturer_name,const int &number_of_lectures,const std::string &type_of_lecture)
{
    this->assignments[lecturer_name].emplace_back(std::make_tuple(course_name,number_of_lectures,type_of_lecture));
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

void Problem::events_assignment()
{
    for(const auto &assignment_pair:this->assignments)
    {
        auto lecturer=std::find_if(this->lecturers.begin(),this->lecturers.end(),[&](const Lecturer &lecturer) {return lecturer.get_name()==assignment_pair.first;});
        for(const auto &assignment:assignment_pair.second)
        {   
            std::cout<<std::get<0>(assignment)<<" "<<std::get<1>(assignment)<<" "<<std::get<2>(assignment)<<std::endl;
            auto course=std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return std::get<0>(assignment)==c.get_name();});
            auto course_type=get_course_type(std::get<2>(assignment));
            if(course_type==TYPE::THEORY || course_type==TYPE::TUTORING)
            {
                for(int k=0;k<int(std::get<1>(assignment));k++)
                {
                    std::find_if(this->events.begin(),this->events.end(),[&](const Event &event) {return event.get_type()==course_type && event.get_lecture_id()==k && event.is_events_course(*course);})->setLecturer(&this->lecturers[lecturer-this->lecturers.begin()]);
                    lecturer->add_event(std::find_if(this->events.begin(),this->events.end(),[&](const Event &event) {return event.get_type()==course_type && event.get_lecture_id()==k && event.is_events_course(*course);})-this->events.begin());
                }
            }
            else
            {
                for(int hour=course->get_lab_hours_in_use();hour<course->get_lab_hours_in_use()+std::get<1>(assignment);hour++)
                {
                    std::find_if(this->events.begin(),this->events.end(),[&](const Event &event) {return event.get_type()==course_type && event.get_lecture_id()==hour && event.is_events_course(*course);})->setLecturer(&this->lecturers[lecturer-this->lecturers.begin()]);
                    lecturer->add_event(std::find_if(this->events.begin(),this->events.end(),[&](const Event &event) {return event.get_type()==course_type && event.get_lecture_id()==hour && event.is_events_course(*course);})-this->events.begin());
                }
                course->add_lab_used_hour(std::get<1>(assignment));
            }
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
    os<<"*** Dit Dataset ***"<<std::endl;
    os<<"Semesters:"<<problem.semesters<<std::endl;
    os<<"Events:"<<problem.events.size()<<std::endl;
    os<<"Courses:"<<problem.number_of_courses()<<std::endl;
    os<<"Lecturers:"<<problem.number_of_lecturers()<<std::endl;
    os<<"Curricula:"<<problem.number_of_curricula()<<std::endl;
    os<<"Rooms:"<<problem.number_of_rooms()<<std::endl<<std::endl;
    os<<"===== Events ======"<<std::endl;
    os<<problem.events.size()<<std::endl;
    for(const auto &event:problem.events)
    {
        os<<"E:"<<std::string(event)<<std::endl;
    }
    os<<std::endl<<std::endl;
    return os;
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


void Problem::change_problem_path(const std:: vector <std::string> &files)
{
    Problem::path_to_datasets="";
    fs::path path_handler(".");
    for(auto &path_component:files)
    {
        path_handler.append(path_component);
    }
    Problem::path_to_datasets=path_handler.string();
}

std::string Problem::path_to_datasets="";