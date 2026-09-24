import rclpy
from rclpy.node import Node

from action_msgs.msg import GoalStatusArray
from std_msgs.msg import String


class NavStatusBridge(Node):

    def __init__(self):
        super().__init__("nav_status_bridge")

        self.status_pub = self.create_publisher(
            String,
            "/navigation_status",
            10
        )

        self.create_subscription(
            GoalStatusArray,
            "/navigate_to_pose/_action/status",
            self.status_callback,
            10
        )

        self.last_status = "IDLE"

        self.publish_status("IDLE")

        self.get_logger().info(
            "Navigation status bridge started"
        )

    def status_callback(self, msg):

        if not msg.status_list:
            self.publish_status("IDLE")
            return

        status = msg.status_list[-1].status

        status_names = {
            1: "ACCEPTED",
            2: "EXECUTING",
            3: "CANCELING",
            4: "SUCCEEDED",
            5: "CANCELED",
            6: "FAILED",
            0: "UNKNOWN"
        }

        new_status = status_names.get(
            status,
            "UNKNOWN"
        )

        self.publish_status(new_status)

    def publish_status(self, status):

        if status != self.last_status:

            msg = String()
            msg.data = status

            self.status_pub.publish(msg)

            self.last_status = status

            self.get_logger().info(
                f"Navigation status: {status}"
            )


def main(args=None):

    rclpy.init(args=args)

    node = NavStatusBridge()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
