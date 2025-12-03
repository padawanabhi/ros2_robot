#!/usr/bin/env python3
"""
Navigation node for TurtleBot3
Subscribes to goal poses and publishes velocity commands
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformListener, Buffer
import math


class NavigationNode(Node):
    def __init__(self):
        super().__init__('navigation_node')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscribers
        self.goal_pose_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_pose_callback,
            10
        )
        
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        
        # TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # State variables
        self.current_pose = None
        self.goal_pose = None
        self.linear_speed = 0.2  # m/s
        self.angular_speed = 0.5  # rad/s
        self.position_tolerance = 0.1  # m
        self.orientation_tolerance = 0.1  # rad
        
        # Control timer
        self.control_timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info('Navigation node started')
    
    def odom_callback(self, msg):
        """Update current pose from odometry"""
        self.current_pose = msg.pose.pose
    
    def goal_pose_callback(self, msg):
        """Handle new goal pose"""
        self.goal_pose = msg.pose
        self.get_logger().info(f'New goal received: x={msg.pose.position.x:.2f}, y={msg.pose.position.y:.2f}')
    
    def control_loop(self):
        """Main control loop"""
        if self.current_pose is None or self.goal_pose is None:
            return
        
        # Calculate distance and angle to goal
        dx = self.goal_pose.position.x - self.current_pose.position.x
        dy = self.goal_pose.position.y - self.current_pose.position.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate desired heading
        desired_heading = math.atan2(dy, dx)
        
        # Get current orientation (yaw)
        current_yaw = self.quaternion_to_yaw(self.current_pose.orientation)
        
        # Calculate angle difference
        angle_diff = self.normalize_angle(desired_heading - current_yaw)
        
        # Create velocity command
        cmd = Twist()
        
        if distance > self.position_tolerance:
            # Move towards goal
            if abs(angle_diff) > self.orientation_tolerance:
                # Rotate to face goal
                cmd.angular.z = self.angular_speed if angle_diff > 0 else -self.angular_speed
            else:
                # Move forward
                cmd.linear.x = min(self.linear_speed, distance * 0.5)
                cmd.angular.z = angle_diff * 0.5  # Fine-tune orientation
        else:
            # Reached position, now align orientation
            goal_yaw = self.quaternion_to_yaw(self.goal_pose.orientation)
            final_angle_diff = self.normalize_angle(goal_yaw - current_yaw)
            
            if abs(final_angle_diff) > self.orientation_tolerance:
                cmd.angular.z = self.angular_speed if final_angle_diff > 0 else -self.angular_speed
            else:
                # Goal reached
                self.get_logger().info('Goal reached!')
                self.goal_pose = None
        
        self.cmd_vel_pub.publish(cmd)
    
    def quaternion_to_yaw(self, quaternion):
        """Convert quaternion to yaw angle"""
        siny_cosp = 2.0 * (quaternion.w * quaternion.z + quaternion.x * quaternion.y)
        cosy_cosp = 1.0 - 2.0 * (quaternion.y * quaternion.y + quaternion.z * quaternion.z)
        return math.atan2(siny_cosp, cosy_cosp)
    
    def normalize_angle(self, angle):
        """Normalize angle to [-pi, pi]"""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle


def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

