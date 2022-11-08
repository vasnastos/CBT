#include "problem.hpp"

struct Sol
{
    int period;
    int room;
    Sol(int _period,int _room):period(_period),room(_room) {}
};

class Solution
{
    Problem *problem;
    public:
        std::vector <std::tuple <int,int>> lectures;
        std::vector <std::pair <int,Sol>> _solution;
        Solution(Problem *pr);
        ~Solution();
        int compute_cost()const;
        void save();
        void read(const std::string &filename);
};