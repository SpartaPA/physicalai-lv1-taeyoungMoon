import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'turtle_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pa9',
    maintainer_email='ansxodud23@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'subscribe_pose = turtle_py.subscribe_pose:main',
            'distance_warning = turtle_py.distance_warning:main',
            'square_driver = turtle_py.square_driver:main',
            'builtin_service_client = turtle_py.builtin_service_client:main',
            'rotate_absolute_client = turtle_py.rotate_absolute_client:main',
            'polygon_action_server = turtle_py.polygon_action_server:main',
            'waypoint_publisher = turtle_py.waypoint_publisher:main',
            'qos_sensor_publisher = turtle_py.qos_sensor_publisher:main',
            'qos_subscriber = turtle_py.qos_subscriber:main',
        ],
    },
)
