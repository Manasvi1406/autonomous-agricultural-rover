#!/bin/bash

# ============================================================
# AUTONOMOUS AGRICULTURAL ROVER
# FULL PROJECT ONE-COMMAND LAUNCHER
# ============================================================

WORKSPACE="$HOME/agri_rover_ws"
LOG_DIR="$WORKSPACE/logs/full_project"

mkdir -p "$LOG_DIR"

echo ""
echo "============================================================"
echo "       AUTONOMOUS AGRICULTURAL ROVER"
echo "              FULL PROJECT STARTUP"
echo "============================================================"
echo ""

# ------------------------------------------------------------
# ROS environment
# ------------------------------------------------------------

source /opt/ros/jazzy/setup.bash
source "$WORKSPACE/install/setup.bash"

export GZ_SIM_SYSTEM_PLUGIN_PATH="/opt/ros/jazzy/lib:/opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins:${GZ_SIM_SYSTEM_PLUGIN_PATH:-}"
export LIBGL_ALWAYS_SOFTWARE=1

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

wait_for_topic() {
    local topic="$1"
    local timeout="$2"
    local elapsed=0

    echo "[WAIT] Topic: $topic"

    while [ "$elapsed" -lt "$timeout" ]; do
        if ros2 topic info "$topic" 2>/dev/null | grep -q "Publisher count: [1-9]"; then
            echo "[ OK ] Topic ready: $topic"
            return 0
        fi

        sleep 2
        elapsed=$((elapsed + 2))
    done

    echo "[ERROR] Timeout waiting for topic: $topic"
    return 1
}

# ------------------------------------------------------------
# 1. Navigation foundation
# ------------------------------------------------------------

echo "[1/5] Starting Gazebo + Navigation stack..."

"$WORKSPACE/start_agri_rover.sh" \
    > "$LOG_DIR/navigation_launcher.log" 2>&1 &

NAV_LAUNCHER_PID=$!

echo "[ OK ] Navigation launcher started (PID $NAV_LAUNCHER_PID)"

echo "[WAIT] Waiting for navigation system..."

if ! wait_for_topic "/diff_drive_controller/odom" 120; then
    echo "[ERROR] Navigation startup failed."
    exit 1
fi

if ! wait_for_topic "/scan" 60; then
    echo "[ERROR] LiDAR startup failed."
    exit 1
fi

echo "[ OK ] Navigation foundation ready"
echo ""

# ------------------------------------------------------------
# 2. Agricultural sensors
# ------------------------------------------------------------

echo "[2/5] Starting agricultural sensors..."

ros2 run agri_rover_sensors sensor_simulator \
    > "$LOG_DIR/sensor_simulator.log" 2>&1 &

SENSOR_PID=$!

echo "[ OK ] Sensor simulator started (PID $SENSOR_PID)"

ros2 run agri_rover_sensors data_logger \
    > "$LOG_DIR/data_logger.log" 2>&1 &

LOGGER_PID=$!

echo "[ OK ] Data logger started (PID $LOGGER_PID)"

sleep 3

echo "[ OK ] Agricultural sensors ready"
echo ""

# ------------------------------------------------------------
# 3. Navigation status bridge
# ------------------------------------------------------------

echo "[3/5] Starting navigation status bridge..."

ros2 run agri_rover_sensors nav_status_bridge \
    > "$LOG_DIR/nav_status_bridge.log" 2>&1 &

STATUS_PID=$!

echo "[ OK ] Navigation status bridge started (PID $STATUS_PID)"

sleep 2

# ------------------------------------------------------------
# 4. YOLO detector
# ------------------------------------------------------------

echo "[4/5] Starting YOLO plant detector..."

ros2 run agri_rover_sensors yolo_detector \
    > "$LOG_DIR/yolo_detector.log" 2>&1 &

YOLO_PID=$!

echo "[ OK ] YOLO detector started (PID $YOLO_PID)"

sleep 5

echo "[ OK ] AI plant detection ready"
echo ""

# ------------------------------------------------------------
# 5. Dashboard
# ------------------------------------------------------------

echo "[5/5] Starting agricultural dashboard..."

cd "$WORKSPACE/dashboard"

"$WORKSPACE/dashboard/venv/bin/python" app.py \
    > "$LOG_DIR/dashboard.log" 2>&1 &

DASHBOARD_PID=$!

echo "[ OK ] Dashboard started (PID $DASHBOARD_PID)"

sleep 5

# ------------------------------------------------------------
# Final status
# ------------------------------------------------------------

echo ""
echo "============================================================"
echo "             FULL PROJECT STARTUP COMPLETE"
echo "============================================================"
echo ""
echo "Gazebo / Rover       : READY"
echo "Controllers          : ACTIVE"
echo "LiDAR                : READY"
echo "AMCL                 : ACTIVE"
echo "Nav2                 : ACTIVE"
echo "RViz                 : RUNNING"
echo "Sensors              : RUNNING"
echo "Data Logger          : RUNNING"
echo "Navigation Bridge    : RUNNING"
echo "YOLO Detector        : RUNNING"
echo "Dashboard            : RUNNING"
echo ""
echo "Dashboard:"
echo "  http://127.0.0.1:5000"
echo ""
echo "Logs:"
echo "  $LOG_DIR"
echo ""
echo "============================================================"
echo "       AUTONOMOUS AGRICULTURAL ROVER IS READY"
echo "============================================================"
echo ""

# ------------------------------------------------------------
# Keep launcher alive
# ------------------------------------------------------------

wait
