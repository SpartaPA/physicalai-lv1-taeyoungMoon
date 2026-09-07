#include <chrono>
#include <cmath>
#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "turtlesim/msg/pose.hpp"

using namespace std::chrono_literals;

class TurtleDistancePublisher : public rclcpp::Node
{
public:
    TurtleDistancePublisher()
    : Node("turtle_cpp_distance_publisher")
    {
        // 발행자, 구독자, 타이머 생성
        publisher_ = this->create_publisher<std_msgs::msg::Float32>(
            "/turtle_distance",
            rclcpp::SystemDefaultsQoS()
        );
        subscription_ = 
            this->create_subscription<turtlesim::msg::Pose>(
                "/turtle1/pose",
                rclcpp::SystemDefaultsQoS(),
                std::bind(
                    &TurtleDistancePublisher::pose_callback,
                    this,
                    std::placeholders::_1
                )
            );
        timer_ = this->create_wall_timer(
            100ms,
            std::bind(
                &TurtleDistancePublisher::timer_callback,
                this
            )
        );
    }
private:
    // 콜백 함수와 멤버 변수
    void pose_callback(
        const turtlesim::msg::Pose::SharedPtr msg)
    {
        latest_x_ = msg->x;
        latest_y_ = msg->y;
        has_pose_ = true;
    }

    void timer_callback()
    {
        // 다음 단계에서 거리 계산 및 발행
        if (!has_pose_){
            return;
        }

        std_msgs::msg::Float32 message;

        message.data = static_cast<float>(
            std::hypot(latest_x_, latest_y_)
        );

        publisher_->publish(message);
    }

    float latest_x_{0.0F};
    float latest_y_{0.0F};
    bool has_pose_{false};

    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_;
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscription_;
    rclcpp::TimerBase::SharedPtr timer_;
};


int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node=
        std::make_shared<TurtleDistancePublisher>();
    
    rclcpp::spin(node);

    node.reset();
    rclcpp::shutdown();

    return 0;
}