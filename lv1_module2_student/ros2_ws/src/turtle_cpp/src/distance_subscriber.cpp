#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"

class DistanceSubscriber : public rclcpp::Node
{
public:
    DistanceSubscriber()
    : Node("turtle_cpp_distance_subscriber")
    {
        // 다음 단계에서 구독자 생성
        subscription_ =
        this->create_subscription<std_msgs::msg::Float32>(
        "/turtle_distance",
        rclcpp::SystemDefaultsQoS(),
        std::bind(
            &DistanceSubscriber::distance_callback,
            this,
            std::placeholders::_1
        )
    );
    }

private:
    void distance_callback(
        const std_msgs::msg::Float32::SharedPtr msg)
    {
        // 다음 단계에서 msg->data 로그 출력
        RCLCPP_INFO(
            this->get_logger(),
            "원점으로부터의 거리: %.3f",
            msg->data
        );
    }

    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr
        subscription_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node =
        std::make_shared<DistanceSubscriber>();

    rclcpp::spin(node);

    node.reset();
    rclcpp::shutdown();

    return 0;
}