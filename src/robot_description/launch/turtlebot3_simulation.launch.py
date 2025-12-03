import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    """
    Launch file that uses the Ignition Gazebo (ros_gz_sim) compatible launch file.
    This is a wrapper that redirects to turtlebot3_gz_sim.launch.py
    """
    pkg_robot_description = get_package_share_directory('robot_description')
    
    # Include the Ignition Gazebo compatible launch file
    gz_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_robot_description, 'launch', 'turtlebot3_gz_sim.launch.py')
        )
    )
    
    return LaunchDescription([
        gz_sim_launch
    ])

