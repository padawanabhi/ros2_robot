import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Get package directories
    pkg_turtlebot3_navigation = get_package_share_directory('turtlebot3_navigation2')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_file = LaunchConfiguration('map', default=os.path.join(
        pkg_turtlebot3_navigation, 'map', 'map.yaml'
    ))
    
    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=map_file,
        description='Full path to map yaml file to load'
    )
    
    # Launch Nav2
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_file,
            'params_file': os.path.join(
                pkg_turtlebot3_navigation, 'param', 'nav2_params.yaml'
            )
        }.items()
    )
    
    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_map_cmd,
        nav2_launch
    ])

