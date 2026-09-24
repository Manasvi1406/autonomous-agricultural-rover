import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class SensorSimulator(Node):

    def __init__(self):
        super().__init__("sensor_simulator")

        self.soil_pub = self.create_publisher(
            Float32, "/soil_moisture", 10
        )

        self.temp_pub = self.create_publisher(
            Float32, "/temperature", 10
        )

        self.humidity_pub = self.create_publisher(
            Float32, "/humidity", 10
        )

        self.timer = self.create_timer(1.0, self.publish_sensor_data)

        self.get_logger().info("Agricultural sensor simulator started")

    def publish_sensor_data(self):

        soil = random.uniform(35.0, 75.0)
        temperature = random.uniform(22.0, 35.0)
        humidity = random.uniform(45.0, 85.0)

        soil_msg = Float32()
        soil_msg.data = soil

        temp_msg = Float32()
        temp_msg.data = temperature

        humidity_msg = Float32()
        humidity_msg.data = humidity

        self.soil_pub.publish(soil_msg)
        self.temp_pub.publish(temp_msg)
        self.humidity_pub.publish(humidity_msg)

        self.get_logger().info(
            f"Soil: {soil:.1f}% | "
            f"Temperature: {temperature:.1f}°C | "
            f"Humidity: {humidity:.1f}%"
        )


def main(args=None):
    rclpy.init(args=args)

    node = SensorSimulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
