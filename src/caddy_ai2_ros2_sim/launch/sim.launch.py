# Copyright (c) 2026, racarla96 - Rafael Carbonell Lázaro
# This work is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
# https://creativecommons.org/licenses/by/4.0/legalcode
"""
Single entry point of the Caddy AI2 simulation (Gazebo Harmonic).

Starts, depending on the arguments:
  Gazebo + robot + controllers + EKF          (always)
  EasyNav navigation                          (nav:=2d | 3d)
  downsampled Helios cloud for remote RViz    (remote_viz:=true)

Examples:
    # Simulation only, test world
    ros2 launch caddy_ai2_ros2_sim sim.launch.py

    # Parking garage with 3D navigation, on a machine without a display (e.g. a lab server)
    ros2 launch caddy_ai2_ros2_sim sim.launch.py \
        world:=parking_garage.sdf headless:=true nav:=3d remote_viz:=true

    # 2D navigation in the test world, with a saved map
    ros2 launch caddy_ai2_ros2_sim sim.launch.py world:=navigation_test.sdf nav:=2d

The robot is spawned at (x, y, yaw). In the parking garage (0, 0) is the ground floor.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


def _include(pkg, *path, **kwargs):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(get_package_share_directory(pkg), *path)),
        **kwargs)


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    headless = LaunchConfiguration('headless')
    nav = LaunchConfiguration('nav')

    # RViz needs a display: never start it in headless mode
    use_rviz = PythonExpression(
        ["'false' if '", headless, "' == 'true' else '", LaunchConfiguration('use_rviz'), "'"])

    return LaunchDescription([
        # ── World and robot ───────────────────────────────────────────────────────────────
        DeclareLaunchArgument('world', default_value='caddy_ai2_world.sdf',
                              description='World SDF in caddy_ai2_ros2_gazebo_simulation/description/world'),
        DeclareLaunchArgument('robot_name', default_value='caddy_ai2'),
        DeclareLaunchArgument('namespace', default_value='caddy_ai2'),
        DeclareLaunchArgument('prefix', default_value=''),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('z', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        # ── Options ───────────────────────────────────────────────────────────────────────
        DeclareLaunchArgument('use_localization', default_value='true',
                              description='Run the EKF (odom->base_footprint). Required by EasyNav'),
        DeclareLaunchArgument('use_rviz', default_value='true',
                              description='Start RViz (ignored when headless:=true)'),
        DeclareLaunchArgument('headless', default_value='false',
                              description='Gazebo server only, EGL rendering, no GUI (needs no display)'),
        DeclareLaunchArgument('nav', default_value='none',
                              description="EasyNav: 'none', '2d' (costmap) or '3d' (NavMap + Helios)"),
        DeclareLaunchArgument('remote_viz', default_value='false',
                              description='Publish the downsampled Helios cloud for RViz over a tunnel'),

        # Gazebo server without GUI; read by world.launch.py (see GZ_SIM_EXTRA_ARGS there)
        SetEnvironmentVariable('GZ_SIM_EXTRA_ARGS', '-s --headless-rendering',
                               condition=IfCondition(headless)),

        # ── Gazebo + robot + controllers ──────────────────────────────────────────────────
        _include(
            'caddy_ai2_ros2_gazebo_simulation', 'bringup', 'launch', 'simulation.launch.py',
            launch_arguments={
                'world': LaunchConfiguration('world'),
                'robot_name': LaunchConfiguration('robot_name'),
                'namespace': namespace,
                'prefix': LaunchConfiguration('prefix'),
                'x': LaunchConfiguration('x'),
                'y': LaunchConfiguration('y'),
                'z': LaunchConfiguration('z'),
                'yaw': LaunchConfiguration('yaw'),
                # Must be forwarded: otherwise simulation.launch.py keeps its own default
                # ('false'), the controller keeps publishing odom->base_footprint even when
                # the EKF runs, and the two fight over the same transform (constant "jump back
                # in time" TF resets that break AMCL and slam_toolbox).
                'use_localization': LaunchConfiguration('use_localization'),
                'use_rviz': use_rviz,
            }.items()),

        # ── EKF: wheel odometry + IMU -> odom/filtered and odom->base_footprint ───────────
        _include(
            'caddy_ai2_ros2_localization', 'launch', 'ekf_gazebo.launch.py',
            launch_arguments={'namespace': namespace}.items(),
            condition=IfCondition(LaunchConfiguration('use_localization'))),

        # ── EasyNav: its launches only start navigation, the simulation is started above ──
        _include(
            'caddy_ai2_ros2_navigation', 'launch', 'navigation_3d.launch.py',
            condition=IfCondition(PythonExpression(["'", nav, "' == '3d'"]))),
        _include(
            'caddy_ai2_ros2_navigation', 'launch', 'navigation.launch.py',
            condition=IfCondition(PythonExpression(["'", nav, "' == '2d'"]))),

        # ── Helios cloud for remote RViz ──────────────────────────────────────────────────
        _include(
            'caddy_ai2_ros2_navigation', 'launch', 'remote_viz.launch.py',
            condition=IfCondition(LaunchConfiguration('remote_viz'))),
    ])
