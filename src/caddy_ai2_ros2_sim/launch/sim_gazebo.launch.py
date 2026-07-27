from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    gz_share  = get_package_share_directory('caddy_ai2_ros2_gazebo_simulation')
    loc_share = get_package_share_directory('caddy_ai2_ros2_localization')

    return LaunchDescription([
        DeclareLaunchArgument('world',      default_value='caddy_ai2_world.sdf'),
        DeclareLaunchArgument('robot_name', default_value='caddy_ai2'),
        DeclareLaunchArgument('namespace',  default_value='caddy_ai2'),
        DeclareLaunchArgument('prefix',     default_value=''),
        DeclareLaunchArgument('x',          default_value='0.0'),
        DeclareLaunchArgument('y',          default_value='0.0'),
        DeclareLaunchArgument('z',          default_value='0.0'),
        DeclareLaunchArgument('yaw',        default_value='0.0'),
        DeclareLaunchArgument('use_localization', default_value='false',
                              description='Launch EKF localization node'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gz_share, 'bringup', 'launch', 'simulation.launch.py')
            ),
            launch_arguments={
                'world':      LaunchConfiguration('world'),
                'robot_name': LaunchConfiguration('robot_name'),
                'namespace':  LaunchConfiguration('namespace'),
                'prefix':     LaunchConfiguration('prefix'),
                'x':          LaunchConfiguration('x'),
                'y':          LaunchConfiguration('y'),
                'z':          LaunchConfiguration('z'),
                'yaw':        LaunchConfiguration('yaw'),
            }.items(),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(loc_share, 'launch', 'ekf_gazebo.launch.py')
            ),
            launch_arguments={
                'namespace': LaunchConfiguration('namespace'),
            }.items(),
            condition=IfCondition(LaunchConfiguration('use_localization')),
        ),
    ])
