#include <algorithm>
#include <cctype>
#include <locale>

static inline void ltrim(std::string &s)
{
    s.erase(s.begin(),std::find_if(s.begin(),s.end(),[](unsigned char ch){return !std::isspace(ch);}));
}

static inline void rtrim(std::string &s)
{
    s.erase(std::find_if(s.rbegin(),s.rend(),[](unsigned char ch){return !std::isspace(ch);}).base(),s.end());
}

std::string trim(std::string &s)
{
    ltrim(s);
    rtrim(s);
    return s;
}

std::string upper(const std::string &s)
{
    std::string newstring=s;
    std::for_each(newstring.begin(),newstring.end(),[](char &c) {c=::toupper(c);});
    std::cout<<newstring<<std::endl;
    return newstring;
}