#include <vector>
#include <map>
#include <memory>
#include <algorithm>
#include <iterator>

class Graph
{
    private:
        std::map <int,std::vector <int>> _nodes;
        std::vector <std::pair <int,int>> _edges;
    public:
        Graph();
        ~Graph();

        int number_of_nodes();
        int number_of_edges();
        void add_node(const int &node);
        void add_edge(const int &node1,const int &node2);
        void clear();
        std::shared_ptr <std::vector <int>> neighbors(int i);
        std::shared_ptr <std::vector <std::pair <int,int>>> edges();
        std::vector <int> nodes();
        friend std::ostream &operator<<(std::ostream &os,const Graph &g);
};