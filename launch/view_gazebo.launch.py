#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory('piklet_description')

    display_launch = os.path.join(pkg_share, "launch", "display.launch.py")

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(display_launch),
            launch_arguments={
                'sim': 'true',
                'use_sim_time': 'true'
            }.items()
        )
    ])
