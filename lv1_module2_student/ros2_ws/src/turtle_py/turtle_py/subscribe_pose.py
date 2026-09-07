import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool, Trigger
from turtlesim.msg import Pose
from rcl_interfaces.msg import SetParametersResult





class TurtleDistancePublisher (Node):
    def __init__(self):
        super().__init__('turtle_distance_publisher')
        #아직 pose 메세지를 받지 않았다는 의미
        self.latest_pose = None
        self.home_pose = None
        self.declare_parameter('start_enabled', False)
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 0.8)
        self.driving_enabled = self.get_parameter('start_enabled').value

        # 발행 주기를 파라미터로 선언. 10Hz
        self.declare_parameter('publish_rate', 10.0)
        publish_rate = self.get_parameter('publish_rate').value

        # /turtle1/pose 구독자
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            qos_profile_system_default
        )

        # /turtle_distance 발행자
        self.publisher = self.create_publisher(
            Float32,
            '/turtle_distance',
            qos_profile_system_default
        )
        self.cmd_vel_publisher = self.create_publisher(
            Twist, '/turtle1/cmd_vel', qos_profile_system_default
        )
        self.enable_service = self.create_service(
            SetBool, 'enable_driving', self.enable_driving_callback
        )
        self.home_service = self.create_service(
            Trigger, 'save_home', self.save_home_callback
        )

        # 10Hz = 0.1s
        timer_period = 1.0 / publish_rate
        self.timer = self.create_timer(
            timer_period,
            self.timer_callback
        )
        self.add_on_set_parameters_callback(
            self.parameter_callback
        )

    def pose_callback(self, msg):
        # 구독 콜백은 최신 자세를 저장만 함 
        self.latest_pose = msg

    def timer_callback(self):
        #아직 pose를 받지 않았다면 발행하지 않음
        if self.latest_pose is None:
            return

        x = self.latest_pose.x
        y = self.latest_pose.y

        distance = math.sqrt(x * x + y * y)

        message = Float32()
        message.data = float(distance)

        self.publisher.publish(message)

        if self.driving_enabled:
            command = Twist()
            command.linear.x = float(self.get_parameter('linear_speed').value)
            command.angular.z = float(self.get_parameter('angular_speed').value)
            self.cmd_vel_publisher.publish(command)

    def enable_driving_callback(self, request, response):
        self.driving_enabled = bool(request.data)
        if not self.driving_enabled:
            self.cmd_vel_publisher.publish(Twist())
        response.success = True
        response.message = 'driving enabled' if self.driving_enabled else 'driving disabled'
        return response

    def save_home_callback(self, request, response):
        del request
        if self.latest_pose is None:
            response.success = False
            response.message = 'pose has not been received yet'
            return response
        self.home_pose = (
            float(self.latest_pose.x),
            float(self.latest_pose.y),
            float(self.latest_pose.theta),
        )
        response.success = True
        response.message = (
            f'home saved: x={self.home_pose[0]:.3f}, '
            f'y={self.home_pose[1]:.3f}, theta={self.home_pose[2]:.3f}'
        )
        return response

    def parameter_callback(self, parameters):
        for parameter in parameters:
            if parameter.name == 'publish_rate':
                new_rate = float(parameter.value)

                if new_rate <= 0.0:
                    return SetParametersResult(
                        successful=False,
                        reason='publish_rate must be greater than zero'
                    )

                self.destroy_timer(self.timer)

                self.timer = self.create_timer(
                    1.0 / new_rate,
                    self.timer_callback
                )

        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleDistancePublisher()

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
