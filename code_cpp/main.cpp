#include "core.hpp"

std::string select_dataset()
{
    int j;
    std::cout<<"====== Datasets ======"<<std::endl;
    for(int i=0,t=Problem::dataset_source.size();i<t;i++)
    {
        std::cout<<i+1<<"."<<Problem::dataset_source[i]<<std::endl;
    }
    std::cout<<"Select dataset:";
    std::cin>>j;
    try
    {
        return Problem::dataset_source[j];
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
        exit(EXIT_FAILURE);
    }
}

// ------------------------ Scenarios -----------------------------------------

void scenario1()
{
    // validate toy dataset, proceed to next phase
    Problem::init_source();
    fs::path full_path_to_toy_dataset(Problem::path_to_datasets);
    full_path_to_toy_dataset.append("Udine2.ectt");
    Problem problem(full_path_to_toy_dataset.string());
    problem.summary();
}


void scenario_2()
{
    
}



int main()
{
    scenario1(); // Test metrics in toy sample of udine
    return EXIT_SUCCESS;
}