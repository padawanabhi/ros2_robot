#!/usr/bin/env python3
"""
Path planning node for TurtleBot3
Implements basic path planning algorithms
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import Path, OccupancyGrid
from std_msgs.msg import Header
from visualization_msgs.msg import Marker
import math


class PathPlannerNode(Node):
    def __init__(self):
        super().__init__('path_planner_node')
        
        # Publishers
        self.path_pub = self.create_publisher(Path, '/planned_path', 10)
        self.marker_pub = self.create_publisher(Marker, '/path_marker', 10)
        
        # Subscribers
        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )
        
        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )
        
        # State variables
        self.map_data = None
        self.map_metadata = None
        self.start_pose = None
        self.goal_pose = None
        
        self.get_logger().info('Path planner node started')
    
    def map_callback(self, msg):
        """Update map data"""
        self.map_data = msg.data
        self.map_metadata = msg.info
        self.get_logger().info('Map received')
    
    def goal_callback(self, msg):
        """Handle goal pose and plan path"""
        self.goal_pose = msg
        if self.map_data is not None:
            self.plan_path()
    
    def plan_path(self):
        """Plan path from start to goal using simple straight-line planning"""
        if self.goal_pose is None or self.map_data is None:
            return
        
        # For now, implement a simple straight-line path
        # In a full implementation, you would use A*, RRT, or other algorithms
        
        path = Path()
        path.header = Header()
        path.header.frame_id = 'map'
        path.header.stamp = self.get_clock().now().to_msg()
        
        # Create a simple straight-line path with intermediate points
        num_points = 10
        if self.start_pose is not None:
            start_x = self.start_pose.position.x
            start_y = self.start_pose.position.y
        else:
            # Default start at origin
            start_x = 0.0
            start_y = 0.0
        
        goal_x = self.goal_pose.pose.position.x
        goal_y = self.goal_pose.pose.position.y
        
        for i in range(num_points + 1):
            t = i / num_points
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = start_x + t * (goal_x - start_x)
            pose.pose.position.y = start_y + t * (goal_y - start_y)
            pose.pose.position.z = 0.0
            pose.pose.orientation = self.goal_pose.pose.orientation
            
            path.poses.append(pose)
        
        self.path_pub.publish(path)
        self.publish_path_marker(path)
        self.get_logger().info(f'Path planned with {len(path.poses)} waypoints')
    
    def publish_path_marker(self, path):
        """Publish path as visualization marker"""
        marker = Marker()
        marker.header = path.header
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.05  # Line width
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0
        
        for pose in path.poses:
            point = Point()
            point.x = pose.pose.position.x
            point.y = pose.pose.position.y
            point.z = pose.pose.position.z
            marker.points.append(point)
        
        self.marker_pub.publish(marker)
    
    def world_to_map(self, x, y):
        """Convert world coordinates to map indices"""
        if self.map_metadata is None:
            return None, None
        
        map_x = int((x - self.map_metadata.origin.position.x) / self.map_metadata.resolution)
        map_y = int((y - self.map_metadata.origin.position.y) / self.map_metadata.resolution)
        
        return map_x, map_y
    
    def is_cell_free(self, map_x, map_y):
        """Check if a map cell is free (not occupied)"""
        if self.map_data is None or self.map_metadata is None:
            return True
        
        if map_x < 0 or map_x >= self.map_metadata.width:
            return False
        if map_y < 0 or map_y >= self.map_metadata.height:
            return False
        
        index = map_y * self.map_metadata.width + map_x
        if index >= len(self.map_data):
            return False
        
        # 0 = free, 100 = occupied, -1 = unknown
        return self.map_data[index] == 0


def main(args=None):
    rclpy.init(args=args)
    node = PathPlannerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

