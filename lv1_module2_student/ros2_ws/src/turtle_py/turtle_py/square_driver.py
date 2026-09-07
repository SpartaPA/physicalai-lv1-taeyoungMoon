import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default


class SquareDriver(Node):

    def __init__(self):
        super().__init__('square_driver')

        # /turtle1/cmd_vel 발행자
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            qos_profile_system_default
        )

        # 현재 주행 상태
        self.state = 'forward'

        # 완료한 변의 개수
        self.completed_sides = 0

        # 현재 상태를 시작한 시간
        self.state_start_time = self.get_clock().now()

        # 전체 주행 완료 여부
        self.finished = False

        self.side_length = 4
        self.linear_speed = 1.0
        self.angular_speed = 1.0
        control_period = 0.1

        self.forward_duration = (
            self.side_length / self.linear_speed
        )

        self.turn_duration = (
            (math.pi / 2.0) / self.angular_speed
        )

        self.timer = self.create_timer (
            control_period,
            self.timer_callback
        )

    def timer_callback(self):
        now = self.get_clock().now()

        elapsed = (
            now - self.state_start_time
        ).nanoseconds / 1e9
    
        message = Twist()

        if self.finished:
            self.publisher.publish(message)
            return

        if self.state == 'forward':
            # 전진 명령 설정
            message.linear.x = self.linear_speed
            # 전진 시간이 끝났는지 검사
            message.angular.z = 0.0
            if elapsed >= self.forward_duration:
                self.state = 'turn'
                self.state_start_time = now

                message.linear.x = 0.0
                message.angular.z = 0.0

        elif self.state == 'turn':
            # 제자리 회전 명령 설정
            # 회전 시간이 끝났는지 검사
            message.linear.x = 0.0
            message.angular.z = self.angular_speed

            if elapsed >= self.turn_duration:
                self.completed_sides += 1
                self.state_start_time = now

                #상태가 바뀌는 순간 정지
                message.linear.x = 0.0
                message.angular.z = 0.0

                if self.completed_sides >= 4:
                    self.finished = True
                else:
                    self.state = 'forward'

        self.publisher.publish(message)

    def stop_turtle(self):
        message = Twist()
        self.publisher.publish(message)

def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()

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