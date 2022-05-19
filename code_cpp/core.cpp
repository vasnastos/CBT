#include "core.hpp"

std::vector <std::string> Problem::dataset_source{};

void Problem::init_source()
{
    fs::path pth("");
    for(auto &x:{"..","datasets","udine_datasets"})
    {
        pth.append(x);
    }
    path_to_datasets=pth.string();
    for(auto &entry:fs::recursive_directory_iterator(pth.string()))
    {
        if(fs::is_regular_file(entry.path()))
        {
            Problem::dataset_source.emplace_back(fs::absolute(entry.path()).string());
        }
    }
}

Problem::Problem(const std::string &dataset_name):id(dataset_name)
{
    this->load_udine();
    this->create_graph();
}

std::string Problem::path_to_datasets="";
std::vector <std::string> Problem::dataset_names={
    "Udine1",
    "Udine2",
    "Udine3",
    "Udine4",
    "Udine5",
    "Udine6",
    "Udine7",
    "Udine8",
    "Udine9",
    "Udine10",
    "Udine11",
    "toy"
};

void Problem::load_udine()
{
    if(this->id=="") return;
    

    std::fstream fp(this->id,std::ios::in);
    if(!fp.is_open())
    {
        std::cerr<<"File did not properly"<<std::endl;
        return;
    }

    std::vector <std::string> data;
    std::map <std::string,std::vector <std::string>> curricula_info;
    std::string line,word,category;
    int filecounter=0;
    std::stringstream ss,ss1;

    while(std::getline(fp,line))
    {
        if(line.length()==0) continue;
        if(line=="END.") break;
        if(filecounter<8)
        {
            ss=std::stringstream(line);
            data.clear();
            while(std::getline(ss,word,':'))
            {
                data.emplace_back(word);
            }
            switch(filecounter)
            {
                case 1:
                    this->C=std::stoi(data[1]);
                    break;
                case 2:
                    this->R=std::stoi(data[1]);
                    break;
                case 3:
                    this->D=std::stoi(data[1]);
                    break;
                case 4:
                    this->PPD=std::stoi(data[1]);
                    break;
                case 5:
                    this->CL=std::stoi(data[1]);
                    break;
                case 6:
                    ss1=std::stringstream(data[1]);
                    data.clear();
                    while(std::getline(ss1,word,' '))
                    {
                        data.emplace_back(word);
                    }
                    this->MNDL=std::stoi(data[1]);
                    this->MXDL=std::stoi(data[2]);
                    break;
                case 7:
                    this->UNC=std::stoi(data[1]);
                    break;
                case 8:
                    this->RC=std::stoi(data[1]);
                    break;
                default:
                    break;
            }
            filecounter++;
            continue;
        }

        // Possible Categories on Data
        if(line=="COURSES:")
        {
            category="COURSES";
            continue;
        }
        else if(line=="ROOMS:")
        {
            category="ROOMS";
            continue;
        }
        else if(line=="CURRICULA:")
        {
            category="CURRICULA";
            continue;
        }
        else if(line=="UNAVAILABILITY_CONSTRAINTS:")
        {
            category="UNAVAILABILITY_CONSTRAINTS";
            continue;
        }
        else if(line=="ROOM_CONSTRAINTS:")
        {
            category="ROOM_CONSTRAINTS";
            continue;
        }

        data.clear();
        ss=std::stringstream(line);
        while(std::getline(ss,word,' '))
        {
            data.emplace_back(word);
        }
        if(category=="COURSES")
        {
            this->courses.emplace_back(Course(data[0],data[1],std::stoi(data[2]),std::stoi(data[3]),std::stoi(data[4]),std::stoi(data[5])));
            this->lecturers.insert(data[1]);
        }
        else if(category=="ROOMS")
        {
            this->rooms.emplace_back(Room(data[0],std::stoi(data[1]),std::stoi(data[2])));
        }
        else if(category=="CURRICULA")
        {
            this->curriculas.emplace_back(Curricula(data[0]));
            for(int i=2,t=data.size();i<t;i++)
            {
                auto itr=std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==data[i];});
                itr->set_curricula(data[0]);
                curricula_info[data[0]].emplace_back(data[i]);
            }
        }
        else if(category=="UNAVAILABILITY_CONSTRAINTS")
        {
            this->unavailability_constraints.emplace_back(std::make_tuple(data[0],std::stoi(data[1]),std::stoi(data[2])));
            std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==data[0];})->add_constraint(std::stoi(data[1]),std::stoi(data[2]));
        }
        else if(category=="ROOM_CONSTRAINTS")
        {
            this->room_constraints.emplace_back(std::make_pair(data[0],data[1]));
            std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==data[0];})->add_constraint(data[1]);
        }
    }
    fp.close();
    
    std::string lecture_id,course_full_id;
    for(auto &course:this->courses)
    {
        for(int i=1,t=course.get_number_of_lectures();i<=t;i++)
        {
            course_full_id=course.get_id();
            std::replace(course_full_id.begin(),course_full_id.end(),'c',' ');
            lecture_id="M"+course_full_id+"_"+std::to_string(i);
            this->lectures.emplace_back(Lecture(lecture_id,course));
        }
    }

    for(auto &xp:curricula_info)
    {
        auto itr=std::find_if(this->curriculas.begin(),this->curriculas.end(),[&](const Curricula &c) {return c.get_id()==xp.first;});
        for(auto &course_id:xp.second)
        {
            itr->add_course(*std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==course_id;}));
        }
    }

    this->C=this->courses.size();// number of courses
    this->R=this->rooms.size();// number of rooms
    this->CL=this->curriculas.size();//number of curriculas
    this->UNC-=this->unavailability_constraints.size(); //number of unavailability constraints
    this->RC=this->room_constraints.size();// number of room constraints    
    this->LCS=this->lecturers.size();
    this->P=this->D * this->PPD;
    this->L=this->lectures.size();
}

double Problem::conflict_density(std::string per)
{
    if(per=="lecture")
    {
        int conflict_counter=0;
        for(int i=0;i<this->L;i++)
        {
            for(int j=i+1;j<this->L;j++)
            {
                if(this->lectures[i]==this->lectures[j])
                {
                    continue;
                }
                if(this->lectures[i].course_equality(this->lectures[j]) || this->lectures[i].curricula_equality(this->lectures[j]) || this->lectures[i].teacher_equality(this->lectures[j]))
                {
                    conflict_counter++;
                }
            }
        }
        return static_cast<double>(conflict_counter)/pow(this->L,2);
    }
    else if(per=="course")
    {
        int conflict_counter=0;
        for(int i=0;i<this->C;i++)
        {
            for(int j=i+1;j<this->C;j++)
            {
                if(this->courses[i]==this->courses[j])
                {
                    continue;
                }
                if(this->courses[i].get_lecturer()==this->courses[j].get_lecturer() || this->courses[i].get_curricula()==this->courses[j].get_curricula()) 
                {
                    conflict_counter++;
                }
            }
        }
        return static_cast<double>(conflict_counter)/pow(this->C,2);
    }
    return -1.0;
}
double Problem::teachers_availability(std::string per)
{
    if(per=="lecture")
    return static_cast<double>(std::accumulate(this->lectures.begin(),this->lectures.end(),0,[&](int y,const Lecture &lecture) {return y+lecture.valid_periods(this->D,this->PPD);}))/(this->L*this->P);
    else if(per=="course")
    return static_cast<double>(std::accumulate(this->courses.begin(),this->courses.end(),0,[&](int s,Course &c) {return s+c.valid_periods(this->D,this->PPD);}))/(this->P * this->C);
    return -1;
}

double Problem::room_suitability(std::string per)
{   
    if(per=="lecture")
    {
        return static_cast<double>(std::accumulate(this->lectures.begin(),this->lectures.end(),0,[&](int s,const Lecture &lec) {return s+lec.valid_rooms(this->rooms);}))/(this->L*this->R);
    }
    else if(per=="course")
    {
        std::cout<<static_cast<double>(std::accumulate(this->courses.begin(),this->courses.end(),0,[&](int s,Course &c) {return s+c.valid_rooms(this->rooms);}))<<std::endl;
        return static_cast<double>(std::accumulate(this->courses.begin(),this->courses.end(),0,[&](int s,Course &c) {return s+c.valid_rooms(this->rooms);}))/(this->C * this->R);
    }
    return -1;
}   


std::string Problem::lectures_per_day_per_curriculum()
{
    std::vector <double> lectures_per_day;  
    for(auto &curricula:this->curriculas)
    {
        lectures_per_day.emplace_back(static_cast<double>(curricula.number_of_lectures())/this->D);
    }
    return "["+std::to_string(*std::min_element(lectures_per_day.begin(),lectures_per_day.end()))+" "+std::to_string(std::accumulate(lectures_per_day.begin(),lectures_per_day.end(),0.0,[&](double start_val,double &x) {return start_val+x;})/lectures_per_day.size())+" "+std::to_string(*std::max_element(lectures_per_day.begin(),lectures_per_day.end()))+"]";
}


double Problem::room_occupation(std::string per)
{
    if(per=="room")
    return static_cast<double>(this->L)/(this->R*this->P);
    else if(per=="seats")
    return static_cast<double>(this->total_students())/(this->total_seats()*this->P);
    return -1;
}

int Problem::total_seats()
{
    return std::accumulate(this->rooms.begin(),this->rooms.end(),0,[&](int s,const Room &r) {return s+r.get_capacity();});
}
int Problem::total_students()
{
    return std::accumulate(this->courses.begin(),this->courses.end(),0,[&](int s,const Course &c) {return s+(c.get_students()*c.get_number_of_lectures());});
}
int Problem::min_curriculum_lectures()
{
    return std::min_element(this->curriculas.begin(),this->curriculas.end(),[&](const Curricula &c1,const Curricula &c2) {return c1.number_of_lectures()<c2.number_of_lectures();})->number_of_lectures();
}

int Problem::max_curriculum_lectures()
{
    return std::max_element(this->curriculas.begin(),this->curriculas.end(),[&](const Curricula &c1,const Curricula &c2) {return c1.number_of_lectures()<c2.number_of_lectures();})->number_of_lectures();
}

void Problem::create_graph()
{
    for(auto &lecture:this->lectures)
    {
        this->G.add_node(lecture.get_id());
    }

    for(auto &lecture:this->lectures)
    {
        for(auto &lecture1:this->lectures)
        {
            if(lecture==lecture1) continue;
            if(lecture.course_equality(lecture1) || lecture.teacher_equality(lecture1) || lecture.curricula_equality(lecture1))
            {
                this->G.add_edge(lecture.get_id(),lecture1.get_id());
            }
        }
    }
}

void Problem::summary()
{
    std::cout<<"Problem:"<<this->id<<std::endl;
    
    std::cout<<std::endl<<this->G<<std::endl;
    
    std::cout<<"Number of Students:"<<this->total_students()<<std::endl;
    std::cout<<"Number of seats:"<<this->total_seats()<<std::endl;
    std::cout<<"Min curriculum lectures:"<<this->min_curriculum_lectures()<<std::endl;
    std::cout<<"Max curriculum lectures:"<<this->max_curriculum_lectures()<<std::endl;
    std::cout<<"Lecturers:"<<this->lecturers.size()<<std::endl;
    std::cout<<"Rooms:"<<this->rooms.size()<<std::endl;
    std::cout<<"Periods:"<<this->P<<std::endl<<std::endl;
    
    std::cout<<"Course conflict density:"<<this->conflict_density()<<std::endl;
    std::cout<<"Lecture conflict density:"<<this->conflict_density("lecture")<<std::endl;
    std::cout<<"Teachers availability per course:"<<this->teachers_availability()<<std::endl;
    std::cout<<"Teachers availability per lecture:"<<this->teachers_availability("lecture")<<std::endl;
    std::cout<<"Room Suitability per course:"<<this->room_suitability()<<std::endl;
    std::cout<<"Room Suitability per lecture:"<<this->room_suitability("lecture")<<std::endl;
    std::cout<<"Lectures per day per curriculum:"<<this->lectures_per_day_per_curriculum()<<std::endl;
    std::cout<<"Room Occupation:"<<this->room_occupation()<<std::endl;
    std::cout<<"Per Seat Occupation:"<<this->room_occupation("seats")<<std::endl;
}

Graph::Graph() {}

void Graph::add_node(const std::string &node)
{
    this->nodes.emplace_back(node);
}

void Graph::add_edge(const std::string &e1,const std::string &e2)
{
    this->adj_list[e1].emplace_back(e2);
    this->adj_list[e2].emplace_back(e1);
    this->edges.emplace_back(std::make_pair(e1,e2));
}


bool Graph::has_edge(const std::string &e1,const std::string &e2)
{
    return std::find_if(this->edges.begin(),this->edges.end(),[&](const std::pair <std::string,std::string> &p1) {return (p1.first==e1 && p1.second==e2) || (p1.first==e2 && p1.second==e1);})!=this->edges.end();
}

std::ostream &operator<<(std::ostream &os,const Graph &g)
{
    os<<"       Graph       "<<std::endl;
    for(const auto &noder:g.adj_list)
    {
        os<<"N "<<noder.first<<":[";
        for(auto &n:noder.second)
        {
            os<<n<<" ";
        }
        os<<"]"<<std::endl<<std::endl;
    }
    return os;
}