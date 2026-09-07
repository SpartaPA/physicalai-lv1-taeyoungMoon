import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from std_msgs.msg import Float32

class DistanceWarningSubscriber(Node):

    def __init__(self):
        super().__init__('distance_warning_subscriber')
        self.declare_parameter('warn_distance', 2.5)
        

        self.subscription = self.create_subscription(
            Float32,
            '/turtle_distance',
            self.distance_callback,
            qos_profile_system_default
        )

    def distance_callback(self, msg):
        distance = msg.data
        warn_distance = self.get_parameter('warn_distance').value

        if distance > warn_distance:
            self.get_logger().warning(
                f'원점으로부터의 거리가 임계값을 초과했습니다: {distance:.3f}'
            )

def main(args=None):
    rclpy.init(args=args)
    node = DistanceWarningSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()