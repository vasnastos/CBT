#include "core.hpp"

static inline void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
}

static inline void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}


std::vector <std::string> Problem::dataset_source{};

void Problem::init_source()
{
    fs::path pth("");
    for(auto &x:{"..","datasets","udine_datasets"})
    {
        pth.append(x);
    }
    Problem::path_to_datasets=pth.string();
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
            ltrim(course_full_id);
            rtrim(course_full_id);
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
    this->UNC=this->unavailability_constraints.size(); //number of unavailability constraints
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

void Problem::clear()
{
    this->G.purge();
    this->curriculas.clear();
    this->courses.clear();
    this->lecturers.clear();
    this->lectures.clear();
    this->room_constraints.clear();
    this->unavailability_constraints.clear();
    this->rooms.clear();
    this->room_constraints.clear();

    this->C=-1;// number of courses
    this->R=-1;// number of rooms
    this->CL=-1;//number of curriculas
    this->S=-1;// number of students;
    this->D=-1;// total days
    this->L=-1;// number of lectures
    this->PPD=-1; // periods per day
    this->MNDL=-1;// Min daily lectures
    this->MXDL=-1;//Max Daily lectures
    this->UNC=-1; //number of unavailability constraints
    this->RC=-1;// number of room constraints
    this->LCS=-1; //number of lectures
    this->P=-1; // number of periods

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

int Graph::get_degree(const std::string &v)
{
    return this->adj_list[v].size();
}

std::vector <std::string> Graph::get_neighbors(const std::string &v)
{
    return this->adj_list[v];
}

void Graph::purge()
{
    this->adj_list.clear();
    this->edges.clear();
    this->nodes.clear();
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

Solution::Solution(const std::string &ds_name):cost(0)
{
    this->p=new Problem(ds_name);

    for(int i=0;i<this->p->D;i++)
    {
        for(int j=0;j<this->p->PPD;j++)
        {
            this->speriods_format[i+j]=std::make_pair(i,j);
        }
    }
}

Solution::~Solution()
{
    delete this->p;
}

int Solution::compute_cost()
{
    // Min working days
    return -1;
}

int Solution::compute_normalize_cost()
{
    return -1;
}

bool Solution::feasibility()
{
    return true;
}

void Solution::saturation_largest_first()
{
    std::vector <std::string> todo;
    std::set <std::string>::iterator maxsutitr;
    std::map <std::string,int> degree;
    int v;
    std::string max_degree_vertex;
    int max_degree=-1;
    for(int u=0;u<this->p->L;u++)
    {
        this->speriods[this->p->G.nodes[u]]=-1;
        if(this->p->G.get_degree(this->p->G.nodes[u])>max_degree)
        {
            max_degree=this->p->G.get_degree(this->p->G.nodes[u]);
            max_degree_vertex=this->p->G.nodes[u];
        }
    }
    this->speriods[max_degree_vertex]=0;
    std::map <std::string,int> saturation_level;
    for(int u=0;u<this->p->L;u++)
    {
        if(this->p->G.nodes[u]!=max_degree_vertex)
        {
            todo.push_back(this->p->G.nodes[u]);
        }
        saturation_level[this->p->G.nodes[u]]=0;
        
    }
    saturation_level[max_degree_vertex]=INT_MIN;
    std::vector <std::string> high_satur_nbs=this->p->G.get_neighbors(max_degree_vertex);
    for(auto &x:high_satur_nbs)
    {
        saturation_level[x]++;
    }
    while(!todo.empty())
    {
        int saturation=-1;
        std::string highest_satur_vertex="";
        std::vector <int> saturation_colors;

        for(auto &satur_pair:saturation_level)
        {
            if(satur_pair.second>saturation)
            {
                saturation=satur_pair.second;
                highest_satur_vertex=satur_pair.first;
                saturation_colors.clear();
                for(auto &x:this->p->G.get_neighbors(highest_satur_vertex))
                {
                    saturation_colors.emplace_back(this->speriods[x]);
                }
            }   
        }
        for(auto itr=todo.begin();itr!=todo.end();itr++)
        {
            if(*itr==highest_satur_vertex)
            {
                todo.erase(itr);
                break;
            }
        }
        int lowest_color=0;
        bool done=false;
        while(!done)
        {
            done=true;
            for(auto &c:saturation_colors)
            {
                if(c==lowest_color)
                {
                    lowest_color++;
                    done=false;
                }
            }
        }
        this->speriods[highest_satur_vertex]=lowest_color;

        for(auto &x:this->p->G.get_neighbors(highest_satur_vertex))
        {
            if(saturation_level[x]!=INT_MIN)
            {
                saturation_level[x]++;
            }
        }
        saturation_level[highest_satur_vertex]=INT_MIN;
    }


    for(auto &x:this->speriods)
    {
        std::cout<<"N"<<x.first<<"=>C"<<x.second<<std::endl;
    }
}
