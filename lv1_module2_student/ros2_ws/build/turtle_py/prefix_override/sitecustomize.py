import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/pa9/physicalai-lv1-assignments/lv1_module2_student/ros2_ws/install/turtle_py'
