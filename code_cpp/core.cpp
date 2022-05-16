#include "core.hpp"

std::vector <std::string> Problem::dataset_source{};

void Problem::init_source()
{
    fs::path pth("");
    for(auto &x:{"..","datasets","udine_datasets"})
    {
        pth.append(x);
    }
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
}

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
    std::string line,word,category;
    int filecounter=0;
    std::stringstream ss,ss1;

    while(std::getline(fp,line))
    {
        if(line.length()==0) continue;
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
        }
        else if(line=="ROOMS:")
        {
            category="ROOMS";
        }
        else if(line=="CURRICULA:")
        {
            category="CURRICULA";
        }
        else if(line=="UNAVAILABILITY_CONSTRAINTS:")
        {
            category="UNAVAILABILITY_CONSTRAINTS";
        }
        else if(line=="ROOM_CONSTRAINTS:")
        {
            category="ROOM_CONSTRAINTS";
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
            for(int i=2,t=this->curriculas.size();i<t;i++)
            {
                auto itr=std::find_if(this->courses.begin(),this->courses.end(),[&](const Course &c) {return c.get_id()==data[i];});
                itr->set_curricula(data[0]);
                this->curriculas[this->curriculas.size()-1].add_course(*itr);
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
            lecture_id="M"+std::to_string(std::stoi(course_full_id))+"_"+std::to_string(i);
            this->lectures.emplace_back(Lecture(lecture_id,course));
        }
    }

    this->LCS=this->lecturers.size();
    this->P=this->D * this->PPD;
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
}
double Problem::teachers_availability(std::string per)
{
    if(per=="lecture")
    return static_cast<double>(std::accumulate(this->lectures.begin(),this->lectures.end(),0,[&](int y,const Lecture &lecture) {return y+lecture.valid_periods(this->D,this->PPD);}))/(this->LCS*this->P);
    else if(per=="course")
    return static_cast<double>(std::accumulate(this->courses.begin(),this->courses.end(),0,[&](int s,Course &c) {return s+c.valid_periods(this->D,this->PPD);}))/(this->P * this->C);
    return -1;
}

double Problem::room_suitability(std::string per)
{
    if(per=="lecture")
    return static_cast<double>(std::accumulate(this->lectures.begin(),this->lectures.end(),0,[&](int s,const Lecture &lec) {return s+lec.valid_rooms(this->rooms);}))/this->R;
    else if(per=="course")
    return static_cast<double>(std::accumulate(this->courses.begin(),this->courses.end(),0,[&](int s,Course &c) {return s+c.valid_rooms(this->rooms);}))/(this->P*this->C);
    return -1;
}   


double Problem::lectures_per_day_per_curriculum()
{
    return this->L/(this->P*this->C);
}

double Problem::room_occupation(std::string per="course")
{
    if(per=="lecture")
    return this->L/(this->R*this->P);
    else if(per=="course")
    return this->C/(this->R*this->P);
    return -1;
}