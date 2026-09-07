#include <iostream>  // python의 import 같은 기능 //

// stop_distance.cpp — 로봇의 제동(정지) 거리 계산
//
// 물리: 바퀴와 바닥 사이 마찰이 유일한 제동력이라고 보면
//   감속도 a = mu * g   (mu: 마찰계수, g: 중력가속도 9.81)
//   운동에너지 (1/2)m v^2 이 마찰일 (mu m g d) 로 모두 소모되어 정지하므로
//   d = v^2 / (2 * mu * g)
//
// 빌드: g++ -Wall -std=c++17 stop_distance.cpp -o stop_distance
// 실행: ./stop_distance <속도[m/s]> <마찰계수>
//   인자를 안 주면 값을 직접 입력받는다.

double g_acc = 9.81;

double computeStopDistance(double speed, double mu = 0.15){
    return speed * speed / (2.0 * mu * g_acc);
}

int main() {
    double speed = 0.0;
    double mu = 0.0;

    std::cout << "속도 입력:";
    std::cin >> speed ;

    std::cout << "마찰계수 입력:";
    std::cin >> mu ;

    if (mu <= 0) {
        std::cout << "마찰계수는 0보다 커야 합니다." << std::endl;
        return 1;
    }

    double distance = computeStopDistance(speed, mu);
    std::cout << "정지거리: "<< distance << "m" << std::endl;

    return 0;
}