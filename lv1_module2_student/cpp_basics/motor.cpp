#include <iostream>
#include "motor.hpp"

void Motor::setSpeed(double mps){
    current_speed_=mps;
    std::cout <<"Motor's speed revised to  " << current_speed_<< "m/s" << std::endl;
}