from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # ---------------------------------------------------------
    # Package paths
    # ---------------------------------------------------------
    gazebo_pkg = get_package_share_directory('agri_rover_gazebo')
    description_pkg = get_package_share_directory('agri_rover_description')

    world_file = os.path.join(
        gazebo_pkg,
        'worlds',
        'agri_field.sdf'
    )

    robot_xacro = os.path.join(
        description_pkg,
        'urdf',
        'agri_rover.xacro'
    )

    controllers_file = os.path.join(
        gazebo_pkg,
        'config',
        'controllers.yaml'
    )

    # ---------------------------------------------------------
    # Robot description
    # ---------------------------------------------------------
    robot_description = Command([
        'xacro ',
        robot_xacro
    ])

    # ---------------------------------------------------------
    # Gazebo plugin path
    # ---------------------------------------------------------
    gz_plugin_path = (
        '/opt/ros/jazzy/lib:'
        '/opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins'
    )

    # ---------------------------------------------------------
    # Start Gazebo
    #
    # -r = start simulation immediately (NOT paused)
    # ---------------------------------------------------------
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': ['-r ', world_file]
        }.items()
    )

    # ---------------------------------------------------------
    # ROS 2 <-> Gazebo Clock Bridge
    # ---------------------------------------------------------
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # LiDAR bridge
    # ---------------------------------------------------------
    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Camera image bridge
    # ---------------------------------------------------------
    camera_image_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Camera info bridge
    # ---------------------------------------------------------
    camera_info_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Robot State Publisher
    #
    # Publishes:
    # base_link
    # camera_link
    # lidar_link
    # wheel transforms
    # ---------------------------------------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {
                'robot_description': robot_description,
                'use_sim_time': True
            }
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Spawn rover into Gazebo
    # ---------------------------------------------------------
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic',
            'robot_description',
            '-name',
            'agri_rover'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # LiDAR frame bridge
    #
    # Gazebo publishes:
    # agri_rover/base_link/lidar_link
    #
    # ROS robot TF uses:
    # lidar_link
    #
    # This identity transform connects them.
    # ---------------------------------------------------------
    lidar_frame_bridge = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.0',
            '--yaw', '0.0',
            '--pitch', '0.0',
            '--roll', '0.0',
            '--frame-id', 'lidar_link',
            '--child-frame-id',
            'agri_rover/base_link/lidar_link'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Camera frame bridge
    #
    # Gazebo publishes:
    # agri_rover/base_link/camera_sensor
    #
    # ROS robot TF uses:
    # camera_link
    #
    # This identity transform connects them.
    # ---------------------------------------------------------
    camera_frame_bridge = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.0',
            '--yaw', '0.0',
            '--pitch', '0.0',
            '--roll', '0.0',
            '--frame-id', 'camera_link',
            '--child-frame-id',
            'agri_rover/base_link/camera_sensor'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Joint State Broadcaster
    #
    # Delayed slightly so Gazebo and controller_manager have
    # time to start after the rover is spawned.
    # ---------------------------------------------------------
    joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'joint_state_broadcaster',
                    '--controller-manager',
                    '/controller_manager',
                    '--controller-manager-timeout',
                    '120'
                ],
                output='screen'
            )
        ]
    )

    # ---------------------------------------------------------
    # Differential Drive Controller
    #
    # Started after the joint state broadcaster.
    # ---------------------------------------------------------
    diff_drive_controller = TimerAction(
        period=12.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'diff_drive_controller',
                    '--controller-manager',
                    '/controller_manager',
                    '--controller-manager-timeout',
                    '120'
                ],
                output='screen'
            )
        ]
    )

    # ---------------------------------------------------------
    # Launch everything
    # ---------------------------------------------------------
    return LaunchDescription([

        # Make sure Gazebo can find ros2_control plugin
        SetEnvironmentVariable(
            name='GZ_SIM_SYSTEM_PLUGIN_PATH',
            value=[
                gz_plugin_path,
                ':',
                os.environ.get(
                    'GZ_SIM_SYSTEM_PLUGIN_PATH',
                    ''
                )
            ]
        ),

        # Start Gazebo
        gz_sim,

        # ROS <-> Gazebo bridges
        clock_bridge,
        lidar_bridge,
        camera_image_bridge,
        camera_info_bridge,

        # Robot TF
        robot_state_publisher,

        # Spawn rover
        spawn_entity,

        # Sensor TF bridges
        lidar_frame_bridge,
        camera_frame_bridge,

        # Controllers
        joint_state_broadcaster,
        diff_drive_controller
    ])
