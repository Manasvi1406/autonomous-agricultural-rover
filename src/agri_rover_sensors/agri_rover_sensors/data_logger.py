import csv
import os
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry


class AgriculturalDataLogger(Node):

    def __init__(self):
        super().__init__("agricultural_data_logger")

        self.soil = None
        self.temperature = None
        self.humidity = None
        self.x = None
        self.y = None

        self.create_subscription(
            Float32, "/soil_moisture", self.soil_callback, 10
        )

        self.create_subscription(
            Float32, "/temperature", self.temperature_callback, 10
        )

        self.create_subscription(
            Float32, "/humidity", self.humidity_callback, 10
        )

        self.create_subscription(
            Odometry, "/diff_drive_controller/odom",
            self.odom_callback, 10
        )

        self.csv_path = os.path.expanduser(
            "~/agri_rover_ws/agricultural_data.csv"
        )

        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "timestamp",
                    "x",
                    "y",
                    "soil_moisture",
                    "temperature",
                    "humidity"
                ])

        self.timer = self.create_timer(2.0, self.save_data)

        self.get_logger().info(
            "Agricultural data logger started"
        )

    def soil_callback(self, msg):
        self.soil = msg.data

    def temperature_callback(self, msg):
        self.temperature = msg.data

    def humidity_callback(self, msg):
        self.humidity = msg.data

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def save_data(self):

        if (
            self.soil is None
            or self.temperature is None
            or self.humidity is None
            or self.x is None
            or self.y is None
        ):
            return

        timestamp = datetime.now().isoformat(timespec="seconds")

        with open(self.csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                round(self.x, 3),
                round(self.y, 3),
                round(self.soil, 2),
                round(self.temperature, 2),
                round(self.humidity, 2)
            ])

        self.get_logger().info(
            f"Saved | X: {self.x:.2f} | Y: {self.y:.2f} | "
            f"Soil: {self.soil:.1f}% | "
            f"Temp: {self.temperature:.1f}C | "
            f"Humidity: {self.humidity:.1f}%"
        )


def main(args=None):
    rclpy.init(args=args)

    node = AgriculturalDataLogger()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
