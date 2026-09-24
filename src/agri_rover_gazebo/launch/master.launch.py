from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    SetEnvironmentVariable
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # =========================================================
    # PACKAGE PATHS
    # =========================================================

    gazebo_pkg = get_package_share_directory(
        "agri_rover_gazebo"
    )

    nav2_bringup_pkg = get_package_share_directory(
        "nav2_bringup"
    )

    sim_launch = os.path.join(
        gazebo_pkg,
        "launch",
        "sim.launch.py"
    )

    nav_launch = os.path.join(
        gazebo_pkg,
        "launch",
        "agri_navigation.launch.py"
    )

    map_file = os.path.join(
        gazebo_pkg,
        "maps",
        "agri_field_map.yaml"
    )

    nav2_params = os.path.join(
        gazebo_pkg,
        "config",
        "nav2_params.yaml"
    )

    rviz_config = os.path.join(
        nav2_bringup_pkg,
        "rviz",
        "nav2_default_view.rviz"
    )

    # =========================================================
    # GAZEBO + ROVER
    # =========================================================

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            sim_launch
        )
    )

    # =========================================================
    # MAP SERVER
    # =========================================================

    map_server = TimerAction(
        period=15.0,
        actions=[
            Node(
                package="nav2_map_server",
                executable="map_server",
                name="map_server",
                output="screen",
                parameters=[
                    nav2_params,
                    {
                        "yaml_filename": map_file,
                        "use_sim_time": True
                    }
                ]
            )
        ]
    )

    # =========================================================
    # AMCL LOCALIZATION
    # =========================================================

    amcl = TimerAction(
        period=15.0,
        actions=[
            Node(
                package="nav2_amcl",
                executable="amcl",
                name="amcl",
                output="screen",
                parameters=[
                    nav2_params,
                    {
                        "use_sim_time": True
                    }
                ]
            )
        ]
    )

    # =========================================================
    # LOCALIZATION LIFECYCLE MANAGER
    # =========================================================

    localization_manager = TimerAction(
        period=18.0,
        actions=[
            Node(
                package="nav2_lifecycle_manager",
                executable="lifecycle_manager",
                name="lifecycle_manager_localization",
                output="screen",
                parameters=[
                    nav2_params,
                    {
                        "use_sim_time": True,
                        "autostart": True,
                        "node_names": [
                            "map_server",
                            "amcl"
                        ]
                    }
                ]
            )
        ]
    )

    # =========================================================
    # NAV2
    # =========================================================

    navigation = TimerAction(
        period=22.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    nav_launch
                ),
                launch_arguments={
                    "params_file": nav2_params,
                    "autostart": "True"
                }.items()
            )
        ]
    )

    # =========================================================
    # RVIZ
    # START LAST
    # =========================================================

    rviz = TimerAction(
        period=30.0,
        actions=[
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=[
                    "-d",
                    rviz_config
                ],
                parameters=[
                    {
                        "use_sim_time": True
                    }
                ]
            )
        ]
    )

    # =========================================================
    # RETURN LAUNCH DESCRIPTION
    # =========================================================

    return LaunchDescription([

        # Gazebo plugin path
        SetEnvironmentVariable(
            name="GZ_SIM_SYSTEM_PLUGIN_PATH",
            value=[
                "/opt/ros/jazzy/lib:",
                "/opt/ros/jazzy/opt/gz_sim_vendor/lib/"
                "gz-sim-8/plugins:",
                os.environ.get(
                    "GZ_SIM_SYSTEM_PLUGIN_PATH",
                    ""
                )
            ]
        ),

        # 1. Gazebo + rover
        simulation,

        # 2. Map
        map_server,

        # 3. Localization
        amcl,

        # 4. Localization lifecycle
        localization_manager,

        # 5. Navigation
        navigation,

        # 6. RViz LAST
        rviz
    ])
