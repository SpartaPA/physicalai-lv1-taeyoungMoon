#ifndef SENSOR_HPP
#define SENSOR_HPP

#include <iostream>

// 1. 추상 기반 클래스 (Abstract Base Class)
class Sensor {
public:
    // 가상 소멸자 (Virtual Destructor) - 필수!
    // 다형성을 이용해 Sensor* 포인터로 자식 객체를 delete 할 때 
    // 자식 클래스의 소멸자가 정상 호출되도록 보장합니다.
     virtual ~Sensor() {
        std::cout << "[Sensor] Base Destructor Called" << std::endl;
    }

    // 순수 가상 함수 (Pure Virtual Function)
    // 뒤에 '= 0'을 붙여 추상 클래스로 만들고, 자식 클래스에서 반드시 구현하도록 강제합니다.
    virtual void read() = 0;
};

// 2. Lidar 클래스 (Sensor 상속)
class Lidar : public Sensor {
public:
    ~Lidar() override{
        std::cout << "[Lidar] Destructor Called" << std::endl;
    }

    // 순수 가상 함수 구현 (override 명시)
    void read() override {
        std::cout << "[Lidar] 2D Point Cloud 데이터를 스캔합니다." << std::endl;
    }
};

// 3. Imu 클래스 (Sensor 상속)
class Imu : public Sensor {
public:
    ~Imu() override {
        std::cout << "[Imu] Destructor Called" << std::endl;
    }

    // 순수 가상 함수 구현 (override 명시)
    void read() override {
        std::cout << "[IMU] 관성 가속도 및 각속도 데이터를 측정합니다." << std::endl;
    }
};

#endif // SENSOR_HPP