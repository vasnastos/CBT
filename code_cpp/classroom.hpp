#include <iostream>
#include <sstream>

class Classroom
{
    private:
        std::string id;
        int capacity;
        int building_id;

    public:
        Classroom(std::string rid,int capacity_place,int bid);
        ~Classroom();
        std::string get_id()const;
        operator std::string()const;
};