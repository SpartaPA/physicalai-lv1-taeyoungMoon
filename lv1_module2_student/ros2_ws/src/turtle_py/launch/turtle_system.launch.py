import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    params_file = os.path.join(
        get_package_share_directory('turtle_py'), 'config', 'params.yaml'
    )
    spawn_second = LaunchConfiguration('spawn_second')

    return LaunchDescription([
        DeclareLaunchArgument('spawn_second', default_value='false'),
        Node(
            package='turtlesim', executable='turtlesim_node',
            name='turtlesim', output='screen'
        ),
        Node(
            package='turtle_py', executable='subscribe_pose',
            name='turtle_distance_publisher', parameters=[params_file],
            output='screen'
        ),
        Node(
            package='turtle_py', executable='distance_warning',
            name='turtle_distance_subscriber', parameters=[params_file],
            output='screen'
        ),
        Node(
            package='turtle_py', executable='polygon_action_server',
            name='polygon_action_server', parameters=[params_file],
            output='screen'
        ),
        TimerAction(
            period=2.0,
            actions=[ExecuteProcess(
                cmd=[
                    'ros2', 'service', 'call', '/spawn',
                    'turtlesim/srv/Spawn',
                    "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}",
                ],
                output='screen',
            )],
            condition=IfCondition(spawn_second),
        ),
        Node(
            package='turtle_py', executable='subscribe_pose',
            name='turtle_distance_publisher', namespace='turtle2',
            remappings=[
                ('/turtle1/pose', '/turtle2/pose'),
                ('/turtle1/cmd_vel', '/turtle2/cmd_vel'),
                ('/turtle_distance', 'turtle_distance'),
                ('enable_driving', 'enable_driving'),
                ('save_home', 'save_home'),
            ],
            parameters=[params_file], output='screen',
            condition=IfCondition(spawn_second),
        ),
    ])
