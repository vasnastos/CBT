#include "graph.hpp"

Graph::Graph() {}
Graph::~Graph() {}

int Graph::number_of_nodes() {return this->_nodes.size();}
int Graph::number_of_edges() {return this->_edges.size();}
void Graph::add_node(const int &node) {this->_nodes.insert(std::make_pair(node,std::vector <int>()));}
void Graph::add_edge(const int &node1,const int &node2)
{
    this->_edges.emplace_back(std::make_pair(node1,node2));
}
void Graph::clear()
{
    this->_nodes.clear();
    this->_edges.clear();
}
std::shared_ptr <std::vector <int>> Graph::neighbors(int i) {return std::make_shared<std::vector <int>>(this->_nodes[i]);}
std::shared_ptr <std::vector <std::pair <int,int>>> Graph::edges() {return std::make_shared<std::vector <std::pair <int,int>>>(this->_edges);}

std::vector <int> Graph::nodes()
{
    std::vector <int> all_nodes;
    std::transform(this->_nodes.begin(),this->_nodes.end(),std::back_inserter(all_nodes),[&](const auto &node_pair) {return node_pair.first;});
    return all_nodes;
}

std::ostream &operator<<(std::ostream &os,const Graph &g)
{
    // TODO
}