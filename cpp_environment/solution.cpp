#include "solution.hpp"

Solution::Solution(Problem *pr):problem(pr) {

}

Solution::~Solution() {}

int Solution::compute_cost()const
{
    int cost=0;
    return cost;
}

void Solution::save()
{
    std::fstream fs;
    std::string word;
    fs.open("dit_solution.txt",std::ios::out);
    for(int i=0;i<this->problem->number_of_courses();i++)
    {
        fs<<i<<" "<<this->_solution[i].first<<" "<<this->_solution[i].second.period<<" "<<this->_solution[i].second.room<<std::endl; 
    }
    fs.close();
}

void Solution::read(const std::string &filename)
{
    std::string line,word;
    std::fstream fs;
    fs.open(filename);
    if(!fs.is_open())
    {
        std::cerr<<"File did not open properly"<<std::endl;
        return;
    }
    std::vector <std::string> data;
    while(std::getline(fs,line))
    {
        data.clear();
        std::stringstream ss(line);
        while(std::getline(ss,word,' '))
        {
            data.emplace_back(word);
        }
        this->_solution.emplace_back(std::make_pair(data[1],Sol(std::stoi(data[2]),std::stoi(data[3]))));
    }
    fs.close();
}

std::ostream &operator<<(std::ostream &os,const Solution &solution)
{
    os<<"Events"<<std::endl;
    for(const auto &event:solution.problem->events)
    {
        os<<std::string(event)<<std::endl;
    }
    os<<std::endl<<std::endl;
    return os;
}