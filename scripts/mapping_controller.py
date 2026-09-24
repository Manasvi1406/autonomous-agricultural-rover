#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped


class MappingController(Node):

    def __init__(self):
        super().__init__('mapping_controller')

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.odom_received = False

        self.odom_sub = self.create_subscription(
            Odometry,
            '/diff_drive_controller/odom',
            self.odom_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        sin_yaw = 2.0 * (q.w * q.z + q.x * q.y)
        cos_yaw = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        self.yaw = math.atan2(sin_yaw, cos_yaw)

        self.odom_received = True

    def publish_velocity(self, linear, angular):
        msg = TwistStamped()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.twist.linear.x = linear
        msg.twist.angular.z = angular

        self.cmd_pub.publish(msg)

    def stop(self):
        for _ in range(8):
            self.publish_velocity(0.0, 0.0)
            time.sleep(0.05)

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi

        while angle < -math.pi:
            angle += 2.0 * math.pi

        return angle

    def rotate_to(self, target_degrees):

        target = math.radians(target_degrees)

        self.get_logger().info(
            f'Rotating to {target_degrees:.1f} degrees'
        )

        while rclpy.ok():

            rclpy.spin_once(self, timeout_sec=0.02)

            error = self.normalize_angle(target - self.yaw)

            if abs(error) < math.radians(2.0):
                break

            direction = 1.0 if error > 0 else -1.0

            angular_speed = min(
                0.15,
                max(0.05, abs(error) * 0.5)
            )

            self.publish_velocity(
                0.0,
                direction * angular_speed
            )

        self.stop()

        self.get_logger().info(
            f'Rotation complete: '
            f'Yaw = {math.degrees(self.yaw):.1f} degrees'
        )

    def move_to_y(self, target_y):

        self.get_logger().info(
            f'Moving to Y = {target_y:.2f} m'
        )

        while rclpy.ok():

            rclpy.spin_once(self, timeout_sec=0.02)

            error = target_y - self.y

            if abs(error) < 0.03:
                break

            direction = 1.0 if error > 0 else -1.0

            speed = min(
                0.05,
                max(0.02, abs(error) * 0.5)
            )

            self.publish_velocity(
                direction * speed,
                0.0
            )

        self.stop()

        self.get_logger().info(
            f'Reached X = {self.x:.2f}, '
            f'Y = {self.y:.2f}, '
            f'Yaw = {math.degrees(self.yaw):.1f} degrees'
        )


def main():

    rclpy.init()

    node = MappingController()

    node.get_logger().info(
        'Waiting for odometry...'
    )

    while rclpy.ok() and not node.odom_received:
        rclpy.spin_once(node, timeout_sec=0.1)

    node.get_logger().info(
        f'Start position: '
        f'X={node.x:.2f}, '
        f'Y={node.y:.2f}, '
        f'Yaw={math.degrees(node.yaw):.1f} degrees'
    )

    # STEP 1: Rotate from 0 degrees to +90 degrees
    node.rotate_to(90.0)

    # STEP 2: Move straight north to Y = 3.00 m
    node.move_to_y(3.00)

    node.stop()

    node.get_logger().info(
        'NEXT MAPPING WAYPOINT COMPLETE.'
    )

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
