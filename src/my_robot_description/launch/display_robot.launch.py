import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PythonExpression
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node

def generate_launch_description():
    # Get the share directory of the my_robot_description package
    pkg_my_robot_description = get_package_share_directory('my_robot_description')

    # Path to the URDF file (xacro needs to be processed)
    urdf_file_path = os.path.join(pkg_my_robot_description, 'urdf', 'my_robot.urdf.xacro')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    # Set use_gui to true to use joint_state_publisher_gui, false for joint_state_publisher
    use_gui = LaunchConfiguration('use_gui', default='true') 

    # Add launch argument for launching Gazebo Sim
    declare_launch_gz_cmd = DeclareLaunchArgument(
        'launch_gz',
        default_value='false',
        description='Launch Gazebo Sim (ros_gz_sim) if true')

    launch_gz = LaunchConfiguration('launch_gz', default='false')

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true')

    declare_use_gui_cmd = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='Flag to enable joint_state_publisher_gui')

    # Process the URDF file (xacro)
    robot_description_content = Command(['xacro ', urdf_file_path])

    # Robot State Publisher Node
    # Publishes TF transforms for the robot based on joint states
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time
        }]
    )

    # Joint State Publisher Node
    # Publishes joint states. 
    # If use_gui is true, joint_state_publisher_gui is used which provides a GUI to set joint states.
    # Otherwise, joint_state_publisher is used, which publishes zero for all non-fixed joints.
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=IfCondition(PythonExpression(["'", use_gui, "' == 'false'"])),
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(PythonExpression(["'", use_gui, "' == 'true'"])),
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # RViz2 Node
    # Visualizes the robot model and TF frames
    rviz_config_file = os.path.join(pkg_my_robot_description, 'rviz', 'display.rviz') # We'll create this basic rviz config next
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log', # Use 'screen' for more verbose output
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Optionally launch Gazebo Sim (ros_gz_sim)
    gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gazebo.launch.py')
        ),
        condition=IfCondition(launch_gz)
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_use_gui_cmd,
        declare_launch_gz_cmd,
        robot_state_publisher_node,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node,
        gz_launch
    ])

# A simple RViz config file (display.rviz) needs to be created in a 'rviz' directory
# within the 'my_robot_description' package for this launch file to work fully.
# Example display.rviz content:
# Panels:
#   - Class: rviz_common/Displays
#   - Class: rviz_common/Views
#   - Class: rviz_common/Time
# Visualization Manager:
#   Displays:
#     - Alpha: 0.5
#       Class: rviz_default_plugins/RobotModel
#       Collision Enabled: false
#       Enabled: true
#       Name: RobotModel
#       Robot Description: robot_description
#       TF Prefix: ""
#       Update Interval: 0
#       Value: Lines
#       Visual Enabled: true
#     - Class: rviz_default_plugins/TF
#       Enabled: true
#       Frame Timeout: 15
#       Frames:
#         All Enabled: true
#       Marker Scale: 1
#       Name: TF
#       Show Arrows: true
#       Show Axes: true
#       Show Names: true
#       Tree:
#         base_link: {}
#       Update Interval: 0
#       Value: true
#   Global Options:
#     Fixed Frame: base_link
#     Frame Rate: 30 

# To spawn your robot in Gazebo Sim, after launching with launch_gz:=true, run:
# ros2 run ros_gz_sim create -file <path_to_urdf> -name <robot_name> 