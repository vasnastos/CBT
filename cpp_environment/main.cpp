#include "solution.hpp"


int main(int argc,char **argv)
{
    Problem problem;
    problem.read_instance("dit_winter_pregraduate.txt");
    auto solution=Solution(&problem);
    std::cout<<solution<<std::endl;
    return 0;
}