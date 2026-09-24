from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # Get the Gazebo package location
    gazebo_pkg = get_package_share_directory(
        'agri_rover_gazebo'
    )

    # Path to SLAM Toolbox configuration
    slam_config = os.path.join(
        gazebo_pkg,
        'config',
        'slam_toolbox.yaml'
    )

    # SLAM Toolbox node
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',

        parameters=[
            slam_config,
            {
                'use_sim_time': True
            }
        ],

        # Controller publishes odometry on
        # /diff_drive_controller/odom
        # while SLAM expects /odom.
        remappings=[
            ('/odom', '/diff_drive_controller/odom')
        ]
    )

    return LaunchDescription([
        slam_node
    ])
