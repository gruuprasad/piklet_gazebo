#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'piklet_description'
    pkg_share = get_package_share_directory(pkg_name)

    # Xacro and RViz config
    robot_xacro = PathJoinSubstitution([pkg_share, 'urdf', 'piklet_robot.urdf.xacro'])
    rviz_config = PathJoinSubstitution([pkg_share, 'rviz', 'display_gazebo.rviz'])

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true'
    )

    # Process xacro → urdf string
    robot_description = Command(['xacro ', robot_xacro])

    # Create a node for the ROS-Gazebo bridge to handle message passing
    gz_bridge_params_path = os.path.join(get_package_share_directory(pkg_name),
        'config',
        'gz_bridge.yaml'
    )
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args', '-p',
            f'config_file:={gz_bridge_params_path}'
        ],
        output="screen"
    )

    # Launch Gazebo
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

    # Spawn robot entity into Gazebo
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

    # RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        declare_use_sim_time,
        gazebo,
        rsp,
        spawn_entity,
        bridge
#        rviz,
    ])
