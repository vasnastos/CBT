#include "core.hpp"

Problem::Problem(std::string pid):id(pid) {}

Problem::Problem():id("") {}

std::string Problem::datasets_root="";

void Problem::set_path_to_dataset(const std::string &path_to_ds)
{
    Problem::datasets_root=path_to_ds;
}

void Problem::set_path_to_dataset()
{
    fs::path udpath("");
    for(auto &x:{"Datasets","udine_datasets"})
    {    
        udpath.append(x);
    }
    Problem::datasets_root=udpath.string();

}   

void Problem::load_udine()
{
    fs::path fp("");
    for(auto &x:{Problem::datasets_root,this->id})
    {
        fp.append(x);
    }
    std::string filename=fp.string();
    std::fstream fstream;
    fstream.open(filename,std::ios::in);
    std::string line,word;
    if(!fstream.is_open())
    {
        std::cerr<<"File did not open properly"<<std::endl;
        return;   
    }
    int filecounter=0;
    std::stringstream ss(line);
    std::vector <std::string> data;
    
    std::stringstream ss1;
    std::string category;

    std::vector <std::tuple<std::string,int,int>> unavailability_constraints;
    std::vector <std::pair <std::string,std::string>> room_constrains;

    while(std::getline(fstream,line))
    {
        while(std::getline(ss,word,':'))
        {
            data.emplace_back(word);
        }
        if(line.length()==0) continue;

        if(line=="END.") break;

        if(filecounter<9)
        {
            switch(filecounter)
            {
            case 1:
                this->C=std::stoi(data[1]);
                break;
            case 2:
                this->R=std::stoi(data[1]);
                break;
            case 3:
                this->days=std::stoi(data[1]);
                break;
            case 4:
                this->periodspd=std::stoi(data[1]);
                break;
            case 5:
                this->CR=std::stoi(data[1]);
                break;
            case 6:
                ss1=std::stringstream(data[1]);
                data.clear();
                while(std::getline(ss1,word,' '))
                {
                    data.emplace_back(word);
                }
                this->max_lecturers_in_day=std::stoi(data[1]);
                this->min_lecturers_in_day=std::stoi(data[2]);
                break;
            default:
                break;
            }
            filecounter++;
            data.clear();
            continue;
        }

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
        ss1=std::stringstream(line);
        while(std::getline(ss1,word,' '))
        {
            data.emplace_back(word);
        }
        if(category=="COURSES")
        {
            Course c(data[0],data[1],std::stoi(data[2]),std::stoi(data[3]),std::stoi(data[4]),std::stoi(data[5]));
            for(int i=0,t=std::stoi(data[2]);i<t;i++)
            {
                this->meetings.emplace_back(Meeting(c.get_id()+"Meeting_"+std::to_string(c.get_lecture_current_id()),c));
            }
            this->courses.emplace_back(c);
            if(std::find_if(this->lecturers.begin(),this->lecturers.end(),[&](const Lecturer &lecturer) {return lecturer.get_id()==data[1];})==this->lecturers.end())
            {
                this->lecturers.emplace_back(Lecturer(data[1]));
            }
            std::find_if(this->lecturers.begin(),this->lecturers.end(),[&](const Lecturer &l) {return l.get_id()==data[1];})->add_course(c);
        }
        else if(category=="ROOMS")
        {
            this->classrooms.emplace_back(Classroom(data[0],std::stoi(data[1]),std::stoi(data[2])));
        }
        else if(category=="CURRICULA")
        {
            Curricula c(data[0]);
            for(int i=1,t=data.size();i<t;i++)
            {
                c.add_course(*std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==data[0];}));
            }
            this->curriculas.emplace_back(c);
        }
        else if(category=="UNAVAILABILITY_CONSTRAINT")
        {
            unavailability_constraints.emplace_back(std::make_tuple(data[0],std::stoi(data[1]),std::stoi(data[2])));
        }
        else if(category=="ROOM_CONSTRAINTS")
        {   
            room_constrains.emplace_back(std::make_pair(data[0],data[1]));
        }
    }
    fstream.close();


    // Add constraints
    for(auto &meeting:this->meetings)
    {
        for(auto &cnt:unavailability_constraints)
        {
            if(std::get<0>(cnt)==meeting.get_course_id())
            {
                meeting.add_constraint(std::get<1>(cnt),std::get<2>(cnt));
            }
        }

        for(auto &cnt:room_constrains)
        {
            if(std::get<0>(cnt)==meeting.get_course_id())
            {
                meeting.add_constraint(std::get<1>(cnt));
            }
        }
    }

    for(int i=0;i<this->days;i++){
        for(int j=0;j<this->periodspd;j++)
        {
            this->aperiods.emplace_back(std::make_pair(i,j));
        }
    }

}

double Problem::conflict_density()
{
    int conflict_pair_counter=0;
    for(int i=0,t=this->meetings.size();i<t;i++)
    {
        for(int j=i+1;j<t;j++)
        {
            if(this->meetings.at(i).curricula_equality(this->meetings.at(j)) || this->meetings.at(i).lecturer_equality(this->meetings.at(j)) || this->meetings.at(i).course_equality(this->meetings.at(j)))
            {
                conflict_pair_counter++;
            }
        }
    }
    // return 2*conflict_pair_counter/pow(this->meetings.size(),2)
    return conflict_pair_counter/pow(this->meetings.size(),2);
}

double Problem::teachers_availability()
{
    int conflict_count=0;
    for(auto &meeting:this->meetings)
    {
        for(auto &period_pair:this->aperiods)
        {
            if(meeting.is_period_valid(period_pair))
            {
                conflict_count++;
            }
        }
    }
    // return 2*conflict_count/(this->meetings.size()*this->aperiods.size())
    return conflict_count/(this->meetings.size()*this->aperiods.size());
}

double Problem::room_suitability()
{
    int conflict_count=0;
    for(auto &meeting:this->meetings)
    {
        for(auto &room:this->classrooms)
        {
            if(meeting.is_room_valid(room))
            {
                conflict_count++;
            }
        }
    }
    return static_cast<double>(conflict_count)/this->LC * this->R;
}

int Problem::curricula_index(std::string course_id)
{
    int pos=-1;
    for(auto curricula_itr=this->curriculas.begin();curricula_itr!=this->curriculas.end();curricula_itr++)
    {
        if(curricula_itr->find(course_id))
        {
            pos=this->curriculas.begin()-curricula_itr;        
        }
    }
    return pos;
}

int Problem::lectures_per_day_rate()
{
   return static_cast<double>(this->M * this->CR) /(this->max_lecturers_in_day * this->days);
}

int Problem::room_occupation()
{
    return this->M/(this->R*this->P);
}

 std::vector <std::string> Problem::find_neighbors(const Meeting &m)
 {
    std::vector <std::string> neighbors;
    for(auto &meeting:this->meetings)
    {
        if(meeting==m)
        {
            continue;
        }

        else if(meeting.curricula_equality(m))
        {
            neighbors.emplace_back(m.get_id());
        }

        else if(meeting.course_equality(m))
        {
            neighbors.emplace_back(meeting.get_id());
        }
        else if(meeting.lecturer_equality(m))
        {
            neighbors.emplace_back(meeting.get_id());
        }
    } 
 }

void Problem::create_graph()
{
    for(auto &meeting:this->meetings)
    {
        this->G.add_node(meeting.get_id());
    }

    std::vector <std::string> nbs;
    for(auto &meeting:this->meetings)
    {
        nbs=this->find_neighbors(meeting);
        for(auto &neighbor:nbs)
        {
            this->G.add_edge(meeting.get_id(),neighbor);
        }
    }

    std::cout<<this->G<<std::endl;
}

Graph::Graph() {}

void Graph::add_node(const std::string &lecture)
{
    this->nodes.emplace_back(lecture);
}

void Graph::add_edge(const std::string &l1,const std::string &l2)
{
    this->adj_matrix[l1].emplace_back(l2);
    this->adj_matrix[l2].emplace_back(l1);
    this->edges.emplace_back(std::make_pair(l1,l2));
}

bool Graph::has_edge(const std::string &l1,const std::string &l2)
{
    return std::find_if(this->edges.begin(),this->edges.end(),[&](std::pair <std::string,std::string> &p) {return (p.first==l1 && p.second==l2) || (p.first==l2 && p.second==l1);})!=this->edges.end();
}

std::ostream &operator<<(std::ostream &os,const Graph &g){
    for(auto &x:g.nodes)
    {
        os<<"Node:"<<x<<" =>";
        for(const auto &neighbor:g.adj_matrix.at(x))
        {
            os<<neighbor<<" ";
        }
        os<<std::endl;
    }
}