#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


class AutonomousMission(Node):

    def __init__(self):
        super().__init__('autonomous_agricultural_mission')

        self.client = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose'
        )

        self.waypoints = [
            (0.5, 0.0),
            (1.5, 0.0),
            (1.5, -0.6),
            (0.5, -0.6),
            (-0.5, -0.6),
            (-0.5, 0.0)
        ]

    def create_goal(self, x, y):
        goal = NavigateToPose.Goal()

        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.position.z = 0.0

        # Heading = 0 degrees
        goal.pose.pose.orientation.x = 0.0
        goal.pose.pose.orientation.y = 0.0
        goal.pose.pose.orientation.z = 0.0
        goal.pose.pose.orientation.w = 1.0

        return goal

    def run_mission(self):
        self.get_logger().info('========================================')
        self.get_logger().info(' AUTONOMOUS AGRICULTURAL ROVER MISSION')
        self.get_logger().info('========================================')

        self.get_logger().info('Waiting for Nav2 action server...')

        if not self.client.wait_for_server(timeout_sec=30.0):
            self.get_logger().error('NavigateToPose action server not available.')
            return

        self.get_logger().info('Nav2 action server READY')

        for number, (x, y) in enumerate(self.waypoints, start=1):

            self.get_logger().info(
                f'WAYPOINT {number}/{len(self.waypoints)} '
                f'-> X={x:.2f}, Y={y:.2f}'
            )

            goal = self.create_goal(x, y)

            send_future = self.client.send_goal_async(goal)
            rclpy.spin_until_future_complete(self, send_future)

            goal_handle = send_future.result()

            if goal_handle is None or not goal_handle.accepted:
                self.get_logger().error(
                    f'Waypoint {number} was rejected.'
                )
                return

            self.get_logger().info(
                f'Waypoint {number} accepted. Rover navigating...'
            )

            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)

            result = result_future.result()

            if result is None:
                self.get_logger().error(
                    f'No result received for waypoint {number}.'
                )
                return

            status = result.status

            if status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info(
                    f'✓ WAYPOINT {number} REACHED'
                )
            else:
                self.get_logger().error(
                    f'✗ WAYPOINT {number} FAILED '
                    f'(status={status})'
                )
                self.get_logger().error(
                    'Mission stopped for safety.'
                )
                return

        self.get_logger().info('========================================')
        self.get_logger().info(' ✓ AUTONOMOUS MISSION COMPLETED')
        self.get_logger().info(' ✓ ALL WAYPOINTS REACHED')
        self.get_logger().info(' ✓ ROVER STOPPED')
        self.get_logger().info('========================================')


def main(args=None):
    rclpy.init(args=args)

    node = AutonomousMission()

    try:
        node.run_mission()
    except KeyboardInterrupt:
        node.get_logger().info('Mission stopped by user.')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
