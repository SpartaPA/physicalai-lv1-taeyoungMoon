#include <iostream>
#include <vector>
#include <memory>
#include "Sensor.hpp"

#include <unordered_map>
#include <string>
#include <algorithm>


template <typename T>
T clamp (T value, T min_value, T max_value)
{
    if (value < min_value){
        return min_value;
    }
    if (value > max_value){
        return max_value;
    }
    return value;
}

void leak_test() {
    for (int i=0; i<10; i++){
        Lidar* sensor = new Lidar();
        sensor -> read();
        // delete 생략 
    }
}

void fixed_test() {
    for (int i=0; i<10; i++){
        std::unique_ptr<Lidar>lidar = std::make_unique<Lidar>();
        lidar -> read();
    }
}


int main() {
    std::cout << "=== 1. std::vector<std::unique_ptr<Sensor>> 다형성 루프 실행 ===" << std::endl;
    
    // unique_ptr를 담는 벡터 생성
    std::vector<std::unique_ptr<Sensor>> sensors;

    // Lidar 및 Imu 객체 생성 및 벡터 추가
    sensors.push_back(std::make_unique<Lidar>());
    sensors.push_back(std::make_unique<Imu>());

    // 다형성 루프로 센서 데이터 읽기
    for (const auto& sensor : sensors) {
        sensor->read();
    }

    std::cout << "\n=== 2. 스택 & 힙 종료 시점 관찰 ===" << std::endl;
    // main 함수가 끝날 때 sensors 벡터가 파괴되면서 unique_ptr들이 자동으로 메모리를 해제합니다.
    
    std::cout << "스택 시작" << std::endl;
    {
        Lidar lidar;
        lidar.read();
    } // 지역 객체 lidar가 블록 끝에서 자동 소멸
    std::cout << "스택 종료" << std::endl;

    std::cout << "힙 시작" << std::endl;
    {
        std::unique_ptr<Imu> imu = std::make_unique<Imu>();
        imu->read();
    } // unique_ptr 가 소멸하면서 힙의 Imu 객체도 자동 소멸 
    std::cout << "힙 종료" << std::endl;

    std::cout << "\n=== 3. 센서 최근 측정값 범위 이내 개수 세기 ===" << std::endl;

    std::unordered_map<std::string, double> latest_measurements = {
        {"lidar", 1.25},
        {"imu", 0.08}
    };
    std::cout << "Lidar 최근 측정값: " << latest_measurements["lidar"] << std::endl;
    std::cout << "IMU 최근 측정값: " << latest_measurements["imu"] << std::endl;

    std::vector<double> distance_logs ={
        0.20,
        0.35,
        0.50,
        0.10,
        0.40
    };

    auto count = std::count_if(
        distance_logs.begin(),
        distance_logs.end(),
        [](double distance) {
            return distance <= 0.35;
        }
    );
    std::cout << "목표지점까지 거리 0.35 이내 기록: " << count << "개" << std::endl;

    std::cout << "\n=== 4. 데이터 값 보완 ===" << std::endl;

    double speed = 75.0; /* 실험용 속도 */
    double clamped_speed = clamp (speed, 0.0, 60.0);

    int pixel = 800; /* 실험용 픽셀값 */
    int clamped_pixel = clamp(pixel, 0, 729);

    std::cout << "속도 보정 결과: " << speed << "-> " << clamped_speed << std::endl;
    std::cout << "픽셀 보정 결과: " << pixel << "-> " << clamped_pixel << std::endl;
    std::cout << "\n=== 5. leak test ===" << std::endl;

    //leak_test();
    fixed_test();
    
    std::cout << "\n=== 1. Lidar & Imu 소멸자 출력 ===" << std::endl;

    

    return 0;
}