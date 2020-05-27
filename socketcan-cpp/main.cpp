// gcc -lstdc++ main.cpp
// executable file with the default name a.out which you can run from the terminal using ./a.out
//g++ main.cpp -o main
// ./main

#include <string>
#include <stdio.h>

int main()
{
    std::string bla;
    bla = "BLA BLA";
    printf("%s\n",bla.c_str());
    return 0;
}
