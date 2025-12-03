import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PythonExpression, TextSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Get package directories
    pkg_turtlebot3_description = get_package_share_directory('turtlebot3_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_robot_description = get_package_share_directory('robot_description')
    
    # Get model from environment or use default
    tb3_model = os.environ.get('TURTLEBOT3_MODEL', 'burger')
    
    # Default world file path
    default_world = os.path.join(pkg_robot_description, 'worlds', 'warehouse.sdf')
    
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default=default_world)
    model = LaunchConfiguration('model', default=tb3_model)
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    # Default spawn position in center of warehouse (open area)
    
    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Gazebo world file path (SDF format). Default: warehouse.sdf'
    )
    
    declare_model_cmd = DeclareLaunchArgument(
        'model',
        default_value='burger',
        description='TurtleBot3 model (burger, waffle, waffle_pi)'
    )
    
    declare_x_pose_cmd = DeclareLaunchArgument(
        'x_pose',
        default_value='0.0',
        description='Initial x position of the robot (spawns in center open area)'
    )
    
    declare_y_pose_cmd = DeclareLaunchArgument(
        'y_pose',
        default_value='0.0',
        description='Initial y position of the robot (spawns in center open area)'
    )
    
    # Set TurtleBot3 model environment variable (this will be available after launch starts)
    set_tb3_model = SetEnvironmentVariable(
        'TURTLEBOT3_MODEL',
        model
    )
    
    # Set Gazebo resource path so it can find TurtleBot3 meshes
    # IGN_GAZEBO_RESOURCE_PATH should point to directories containing package folders
    # pkg_turtlebot3_description points to share/turtlebot3_description
    # We need to point to the parent (share/) directory so model://turtlebot3_description resolves correctly
    install_share_dir = os.path.dirname(pkg_turtlebot3_description)
    existing_resource_path = os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')
    
    if existing_resource_path:
        resource_path = install_share_dir + ':' + existing_resource_path
    else:
        resource_path = install_share_dir
    
    set_gz_resource_path = SetEnvironmentVariable(
        'IGN_GAZEBO_RESOURCE_PATH',
        resource_path
    )
    
    # Get URDF file - build path using PythonExpression to handle LaunchConfiguration
    # Note: TurtleBot3 uses .urdf files, not .urdf.xacro
    urdf_file_path = PythonExpression([
        "'", os.path.join(pkg_turtlebot3_description, 'urdf', 'turtlebot3_'), "' + '", model, "' + '.urdf'"
    ])
    
    # Read URDF file directly (no xacro processing needed for .urdf files)
    # But we'll use xacro in case the file has xacro includes
    robot_description_content = Command(['xacro ', urdf_file_path])
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(robot_description_content, value_type=str),
            'use_sim_time': use_sim_time
        }]
    )
    
    # Launch Gazebo Sim with world file
    # Build gz_args to include world file
    gz_args = PythonExpression([
        "'", world, "'"
    ])
    
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': gz_args  # World file path
        }.items()
    )
    
    # Spawn TurtleBot3
    # Use a small delay to ensure Gazebo is ready before spawning
    spawn_entity = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', 'robot_description',
                    '-name', 'turtlebot3',
                    '-x', x_pose,
                    '-y', y_pose,
                    '-z', '0.0'  # Spawn on ground level
                ],
                output='screen'
            )
        ]
    )
    
    # Bridge for cmd_vel (start after a delay to ensure topics are available)
    cmd_vel_bridge = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                     '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
                output='screen'
            )
        ]
    )
    
    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_world_cmd,
        declare_model_cmd,
        declare_x_pose_cmd,
        declare_y_pose_cmd,
        set_tb3_model,
        set_gz_resource_path,
        robot_state_publisher,
        gz_sim,
        spawn_entity,
        cmd_vel_bridge
    ])

