#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('piklet_description')

    # Path to your xacro
    robot_xacro = PathJoinSubstitution([pkg_share, 'urdf', 'piklet_robot.urdf.xacro'])

    # Declare sim_time arg
    use_sim_time = LaunchConfiguration('use_sim_time')
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true'
    )

    # Process the xacro into URDF for Gazebo
    robot_description = Command(['xacro ', robot_xacro])

    # Launch Gazebo (Harmonic, ROS 2 Jazzy uses gz_sim)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-v', '4', '-r', 'empty.sdf'],
        output='screen'
    )

    # Robot State Publisher
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }]
    )

    # Spawn entity into Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-string', robot_description,
            '-name', 'piklet_bot',
            '-allow_renaming', 'true'
        ]
    )

    return LaunchDescription([
        declare_use_sim_time,
        gazebo,
        rsp,
        spawn_entity,
    ])
