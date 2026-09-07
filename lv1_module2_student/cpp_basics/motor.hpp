#pragma once // 중복 include 방지
class Motor{
    public:
        void setSpeed(double mps);
    private:
        double current_speed_ = 0.0;
};
