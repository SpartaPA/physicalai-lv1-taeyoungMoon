#include "iostream"
#include "motor.hpp"

int main(){
    double v = 1.2;

    Motor my_motor;
    my_motor.setSpeed(v);
    std::cout << "motor 속도 = "<< v <<std::endl;
    return 0;
};