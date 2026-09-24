from flask import Flask, render_template, jsonify
import csv
import os
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


app = Flask(__name__)

CSV_FILE = os.path.expanduser(
    "~/agri_rover_ws/agricultural_data.csv"
)

YOLO_CSV_FILE = os.path.expanduser(
    "~/agri_rover_ws/yolo_detections.csv"
)

navigation_status = "IDLE"


class NavigationStatusNode(Node):

    def __init__(self):
        super().__init__("dashboard_navigation_status")

        self.create_subscription(
            String,
            "/navigation_status",
            self.status_callback,
            10
        )

        self.get_logger().info(
            "Dashboard navigation subscriber started"
        )

    def status_callback(self, msg):
        global navigation_status

        navigation_status = msg.data

        self.get_logger().info(
            f"Navigation status: {navigation_status}"
        )


def ros_thread():

    rclpy.init()

    node = NavigationStatusNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


def read_latest_csv(filename):

    if not os.path.exists(filename):
        return None

    try:
        with open(filename, "r", newline="") as file:
            rows = list(csv.DictReader(file))

        if not rows:
            return None

        return rows[-1]

    except Exception:
        return None


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/data")
def get_data():

    latest_sensor = read_latest_csv(CSV_FILE)
    latest_detection = read_latest_csv(YOLO_CSV_FILE)

    return jsonify({
        "status": "online" if latest_sensor else "waiting",
        "data": latest_sensor or {},
        "navigation": navigation_status,
        "ai_detection": latest_detection or {}
    })


if __name__ == "__main__":

    threading.Thread(
        target=ros_thread,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
