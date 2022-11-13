#include "solution.hpp"


int main(int argc,char **argv)
{
    SetConsoleOutputCP(65001);
    Problem::change_problem_path({"..","Datasets","dit_datasets"});

    Problem problem;
    problem.read_instance("dit_winter_pregraduate.txt");
    auto solution=Solution(&problem);
    std::cout<<solution<<std::endl;
    return 0;
}