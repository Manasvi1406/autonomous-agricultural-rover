from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ---------------------------------------------------------
    # Launch arguments
    # ---------------------------------------------------------

    params_file = LaunchConfiguration("params_file")
    autostart = LaunchConfiguration("autostart")

    declare_params_file = DeclareLaunchArgument(
        "params_file",
        default_value=(
            "/home/manasvi/agri_rover_ws/src/"
            "agri_rover_gazebo/config/nav2_params.yaml"
        ),
        description="Full path to the Nav2 parameter file"
    )

    declare_autostart = DeclareLaunchArgument(
        "autostart",
        default_value="True",
        description="Automatically activate Nav2 lifecycle nodes"
    )

    # ---------------------------------------------------------
    # Controller Server
    # ---------------------------------------------------------

    controller_server = Node(
        package="nav2_controller",
        executable="controller_server",
        name="controller_server",
        output="screen",
        parameters=[params_file],
    )

    # ---------------------------------------------------------
    # Smoother Server
    # ---------------------------------------------------------

    smoother_server = Node(
        package="nav2_smoother",
        executable="smoother_server",
        name="smoother_server",
        output="screen",
        parameters=[params_file],
    )

    # ---------------------------------------------------------
    # Planner Server
    # ---------------------------------------------------------

    planner_server = Node(
        package="nav2_planner",
        executable="planner_server",
        name="planner_server",
        output="screen",
        parameters=[params_file],
    )

    # ---------------------------------------------------------
    # Behavior Server
    # ---------------------------------------------------------

    behavior_server = Node(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        output="screen",
        parameters=[params_file],
    )

    # ---------------------------------------------------------
    # BT Navigator
    # ---------------------------------------------------------

    bt_navigator = Node(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        output="screen",
        parameters=[params_file],
    )

    # ---------------------------------------------------------
    # Waypoint Follower
    # ---------------------------------------------------------

    waypoint_follower = Node(
        package="nav2_waypoint_follower",
        executable="waypoint_follower",
        name="waypoint_follower",
        output="screen",
        parameters=[params_file],
    )

    # ---------------------------------------------------------
    # Velocity Smoother
    # ---------------------------------------------------------

    velocity_smoother = Node(
    package="nav2_velocity_smoother",
    executable="velocity_smoother",
    name="velocity_smoother",
    output="screen",
    parameters=[params_file],
    remappings=[
        ("cmd_vel_smoothed", "/diff_drive_controller/cmd_vel")
      ]
    )
    # ---------------------------------------------------------
    # Lifecycle Manager
    # ---------------------------------------------------------

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[
            params_file,
            {
                "autostart": autostart,
                "node_names": [
                    "controller_server",
                    "smoother_server",
                    "planner_server",
                    "behavior_server",
                    "bt_navigator",
                    "waypoint_follower",
                    "velocity_smoother",
                ],
            },
        ],
    )

    # ---------------------------------------------------------
    # Launch description
    # ---------------------------------------------------------

    return LaunchDescription([
        declare_params_file,
        declare_autostart,

        controller_server,
        smoother_server,
        planner_server,
        behavior_server,
        bt_navigator,
        waypoint_follower,
        velocity_smoother,
        lifecycle_manager,
    ])
