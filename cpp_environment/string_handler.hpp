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

// static inline void upper(std::string &s)
// {
//     std::for_each(s.begin(),s.end(),[](unsigned char &c) {c=::toupper(c);});
// }