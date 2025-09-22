from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Paths
    pkg_share = FindPackageShare("piklet_description")

    # Robot description from xacro
    robot_description_content = Command([
        "xacro ",
        PathJoinSubstitution([pkg_share, "urdf", "piklet_robot.urdf.xacro"])
    ])
    robot_description = {"robot_description": robot_description_content}

    # Launch Gazebo Harmonic (empty world)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])
        ]),
        launch_arguments={
            "gz_args": "-r empty.sdf"
        }.items(),
    )

    # Publish robot state to TF
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="screen"
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "robot_description",
            "-name", "piklet_bot",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.1",
        ],
        output="screen"
    )

    # Bridge example (cmd_vel + odom + lidar + camera)
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/piklet_bot/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/piklet_bot/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",
            "/image_raw@sensor_msgs/msg/Image@gz.msgs.Image",
            "/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo"
        ],
        output="screen"
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge
    ])
