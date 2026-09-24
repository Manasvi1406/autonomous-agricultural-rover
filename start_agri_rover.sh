#!/bin/bash


# ============================================================
# AGRICULTURAL ROVER - CLEAN STARTUP
# ROS 2 Jazzy + Gazebo + Localization + Nav2 + RViz
# ============================================================

source /opt/ros/jazzy/setup.bash
source "$HOME/agri_rover_ws/install/setup.bash"

WORKSPACE="$HOME/agri_rover_ws"
LOG_DIR="$WORKSPACE/logs/startup"

mkdir -p "$LOG_DIR"

echo ""
echo "============================================================"
echo "        AUTONOMOUS AGRICULTURAL ROVER"
echo "        CLEAN STARTUP"
echo "============================================================"
echo ""

# ------------------------------------------------------------
# Gazebo plugin path
# ------------------------------------------------------------

export GZ_SIM_SYSTEM_PLUGIN_PATH="/opt/ros/jazzy/lib:/opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins:${GZ_SIM_SYSTEM_PLUGIN_PATH:-}"

# Software OpenGL for WSL/RViz
export LIBGL_ALWAYS_SOFTWARE=1

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

wait_for_topic() {
    local topic="$1"
    local timeout="$2"

    echo "[WAIT] Topic: $topic"

    for ((i=1; i<=timeout; i++)); do
        if ros2 topic info "$topic" >/dev/null 2>&1; then
            echo "[ OK ] Topic available: $topic"
            return 0
        fi
        sleep 1
    done

    echo "[ERROR] Timeout waiting for topic: $topic"
    return 1
}

wait_for_controller() {
    local controller="$1"
    local timeout="$2"

    echo "[WAIT] Controller: $controller"

    for ((i=1; i<=timeout; i++)); do
        if ros2 control list_controllers 2>/dev/null | grep -q "^$controller.*active"; then
            echo "[ OK ] Controller active: $controller"
            return 0
        fi
        sleep 1
    done

    echo "[ERROR] Controller did not become active: $controller"
    return 1
}

wait_for_lifecycle() {
    local node="$1"
    local timeout="$2"

    echo "[WAIT] Lifecycle node: $node"

    for ((i=1; i<=timeout; i++)); do
        if ros2 lifecycle get "$node" 2>/dev/null | grep -q "active"; then
            echo "[ OK ] Active: $node"
            return 0
        fi
        sleep 1
    done

    echo "[ERROR] Lifecycle node did not become active: $node"
    return 1
}

# ------------------------------------------------------------
# 1. Gazebo + Rover
# ------------------------------------------------------------

echo ""
echo "[1/5] Starting Gazebo + Rover..."

ros2 launch agri_rover_gazebo sim.launch.py \
    > "$LOG_DIR/simulation.log" 2>&1 &

SIM_PID=$!

echo "[ OK ] Simulation launch started (PID $SIM_PID)"

# Wait for the controller manager
echo "[WAIT] Controller manager..."

for ((i=1; i<=90; i++)); do
    if ros2 control list_controllers >/dev/null 2>&1; then
        echo "[ OK ] Controller manager available"
        break
    fi
    sleep 1
done

# Verify controllers
wait_for_controller "diff_drive_controller" 60 || exit 1
wait_for_controller "joint_state_broadcaster" 60 || exit 1

# Verify core sensor/odometry topics
wait_for_topic "/diff_drive_controller/odom" 30 || exit 1
wait_for_topic "/scan" 30 || exit 1

echo "[ OK ] Gazebo + controllers + LiDAR ready"

# ------------------------------------------------------------
# 2. Localization
# ------------------------------------------------------------

echo ""
echo "[2/5] Starting Map Server + AMCL..."

ros2 launch nav2_bringup localization_launch.py \
    map:="$WORKSPACE/src/agri_rover_gazebo/maps/agri_field_map.yaml" \
    params_file:="$WORKSPACE/src/agri_rover_gazebo/config/nav2_params.yaml" \
    use_sim_time:=True \
    autostart:=True \
    > "$LOG_DIR/localization.log" 2>&1 &

LOCALIZATION_PID=$!

echo "[ OK ] Localization launch started (PID $LOCALIZATION_PID)"

wait_for_lifecycle "/map_server" 60 || exit 1
wait_for_lifecycle "/amcl" 60 || exit 1

wait_for_topic "/map" 30 || exit 1
wait_for_topic "/amcl_pose" 30 || exit 1

echo "[ OK ] Map Server + AMCL ready"

# ------------------------------------------------------------
# 3. Nav2
# ------------------------------------------------------------

echo ""
echo "[3/5] Starting Nav2..."

ros2 launch agri_rover_gazebo agri_navigation.launch.py \
    params_file:="$WORKSPACE/src/agri_rover_gazebo/config/nav2_params.yaml" \
    autostart:=True \
    > "$LOG_DIR/navigation.log" 2>&1 &

NAV_PID=$!

echo "[ OK ] Nav2 launch started (PID $NAV_PID)"

wait_for_lifecycle "/controller_server" 90 || exit 1
wait_for_lifecycle "/planner_server" 90 || exit 1
wait_for_lifecycle "/bt_navigator" 90 || exit 1
wait_for_lifecycle "/smoother_server" 90 || exit 1
wait_for_lifecycle "/behavior_server" 90 || exit 1
wait_for_lifecycle "/waypoint_follower" 90 || exit 1
wait_for_lifecycle "/velocity_smoother" 90 || exit 1

echo "[ OK ] Nav2 fully active"

# ------------------------------------------------------------
# 4. RViz
# ------------------------------------------------------------

echo ""
echo "[4/5] Starting RViz..."

RVIZ_CONFIG="/opt/ros/jazzy/share/nav2_bringup/rviz/nav2_default_view.rviz"

ros2 run rviz2 rviz2 \
    -d "$RVIZ_CONFIG" \
    > "$LOG_DIR/rviz.log" 2>&1 &

RVIZ_PID=$!

echo "[ OK ] RViz started (PID $RVIZ_PID)"

sleep 5

# ------------------------------------------------------------
# 5. Final status
# ------------------------------------------------------------

echo ""
echo "============================================================"
echo "              ROVER STARTUP COMPLETE"
echo "============================================================"
echo ""
echo "Gazebo              : READY"
echo "Controllers          : ACTIVE"
echo "Odometry             : READY"
echo "LiDAR                : READY"
echo "Map Server           : ACTIVE"
echo "AMCL                 : ACTIVE"
echo "Nav2                 : ACTIVE"
echo "RViz                 : RUNNING"
echo ""
echo "RViz Fixed Frame     : map"
echo ""
echo "Logs:"
echo "  $LOG_DIR/simulation.log"
echo "  $LOG_DIR/localization.log"
echo "  $LOG_DIR/navigation.log"
echo "  $LOG_DIR/rviz.log"
echo ""
echo "============================================================"
echo "      AUTONOMOUS AGRICULTURAL ROVER IS READY"
echo "============================================================"
echo ""

# Keep this launcher alive so background ROS processes remain
# associated with the startup session.
wait
