# ROS2 TurtleBot3 Workspace

This workspace contains packages for running TurtleBot3 in simulation with navigation and path planning capabilities. It includes a custom warehouse world designed for testing navigation algorithms in a dense, realistic environment.

## Prerequisites

### 1. Install ROS2 Humble Dependencies

```bash
# Install available TurtleBot3 packages
sudo apt install ros-humble-turtlebot3-description
sudo apt install ros-humble-turtlebot3-bringup
sudo apt install ros-humble-turtlebot3-msgs

# Install Nav2 navigation stack
sudo apt install ros-humble-nav2-bringup
sudo apt install ros-humble-nav2-common

# Install Gazebo (Ignition Gazebo)
sudo apt install ros-humble-ros-gz-sim
sudo apt install ros-humble-ros-gz-bridge
sudo apt install ros-humble-ros-gz-interfaces
```

### 2. Install TurtleBot3 from Source

**Important Notes**: 
- The `turtlebot3_gazebo` package uses Gazebo Classic which is not compatible with ROS2 Humble's Ignition Gazebo. We skip building it and use `ros_gz_sim` directly instead.
- Some packages like `turtlebot3_node`, `turtlebot3_example`, and `turtlebot3_fake_node` require hardware dependencies (dynamixel_sdk) that aren't available via apt for arm64. These are skipped as they're not needed for simulation.

Install TurtleBot3 packages from source:

**Option A: Install in this workspace (Recommended)**

You can use the provided installation script:
```bash
cd /home/abhishek/Workspace/ros2_robot
./install_turtlebot3.sh
```

Or install manually:
```bash
cd /home/abhishek/Workspace/ros2_robot/src

# Clone TurtleBot3 packages
git clone https://github.com/ROBOTIS-GIT/turtlebot3.git -b humble
git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git -b humble
git clone https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git -b humble

# Install dependencies
cd /home/abhishek/Workspace/ros2_robot
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Build all packages (incompatible/hardware packages will be skipped)
colcon build --symlink-install --packages-skip \
    turtlebot3_gazebo \
    turtlebot3_manipulation_gazebo \
    turtlebot3_node \
    turtlebot3_example \
    turtlebot3_fake_node \
    turtlebot3_simulations \
    turtlebot3
```

**Option B: Install in separate workspace**

```bash
# Create a separate workspace for TurtleBot3
mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws/src

# Clone TurtleBot3 packages
git clone https://github.com/ROBOTIS-GIT/turtlebot3.git -b humble
git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git -b humble
git clone https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git -b humble

# Install dependencies
cd ~/turtlebot3_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Build TurtleBot3 packages (skip incompatible/hardware packages)
colcon build --symlink-install --packages-skip \
    turtlebot3_gazebo \
    turtlebot3_manipulation_gazebo \
    turtlebot3_node \
    turtlebot3_example \
    turtlebot3_fake_node \
    turtlebot3_simulations \
    turtlebot3

# Source the workspace
source ~/turtlebot3_ws/install/setup.bash

# Add to ~/.bashrc for persistence
echo "source ~/turtlebot3_ws/install/setup.bash" >> ~/.bashrc
```

## Setup

### Step 1: Install Prerequisites

Follow the prerequisites section above to install ROS2 Humble dependencies and TurtleBot3 packages.

### Step 2: Set TurtleBot3 Model

Set the TurtleBot3 model (default is burger):
```bash
export TURTLEBOT3_MODEL=burger
# Add to ~/.bashrc for persistence:
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
```

### Step 3: Build the Workspace

Build all packages in this workspace:
```bash
cd /home/abhishek/Workspace/ros2_robot
colcon build --symlink-install
source install/setup.bash
```

**Note**: If you installed TurtleBot3 in a separate workspace, make sure to source it first:
```bash
source ~/turtlebot3_ws/install/setup.bash  # If using separate workspace
source install/setup.bash
```

### Step 4: Verify Installation

Verify that all packages are available:
```bash
# Check TurtleBot3 packages
ros2 pkg list | grep turtlebot3

# Check custom packages
ros2 pkg list | grep robot_description
ros2 pkg list | grep turtlebot3_navigation
ros2 pkg list | grep turtlebot3_path_planning
```

## Usage

### Launch TurtleBot3 Simulation

Launch TurtleBot3 in Gazebo with the warehouse world (default):

```bash
ros2 launch robot_description turtlebot3_simulation.launch.py
```

## Warehouse World

The warehouse world (`warehouse.sdf`) is a custom-designed environment specifically created for testing TurtleBot3 navigation and path planning algorithms.

### World Design

The warehouse world features:

1. **Bounded Environment (10m × 10m)**
   - Four walls creating a closed warehouse space
   - Ground plane for stable robot navigation

2. **Dense Shelf Layout**
   - 24 shelves arranged in a 6×4 grid pattern
   - Each shelf: 0.8m × 0.3m × 0.8m (width × depth × height)
   - Creates narrow aisles and complex navigation paths
   - Shelves positioned at strategic locations to create multiple route options

3. **Partial Dividers**
   - Vertical dividers at x = -2.5m and x = 2.5m (split into top/bottom sections)
   - Horizontal dividers at y = -2.0m and y = 2.0m (split into left/right sections)
   - Dividers create aisles while maintaining connectivity throughout the warehouse
   - Openings in dividers allow navigation between all areas

4. **Center Obstacles**
   - Four small obstacles positioned at corners of the center area
   - Creates additional navigation challenges
   - Ensures clear spawn area at (0, 0)

5. **Spawn Point**
   - Robot spawns at (0, 0) in the center of the warehouse
   - Clear area with no walls or obstacles
   - Allows immediate navigation in all directions

### World Creation Details

The warehouse world was created using SDF (Simulation Description Format) version 1.7, compatible with Ignition Gazebo. Key design decisions:

- **Scale**: Sized appropriately for TurtleBot3 (burger model ~0.2m diameter)
- **Obstacle Density**: Dense enough to challenge path planning while maintaining navigability
- **Connectivity**: All areas are accessible - no completely blocked sections
- **Realistic Layout**: Mimics real warehouse environments with shelves and aisles

**Available worlds:**
- `warehouse.sdf` (default) - Custom warehouse environment with dense shelves and navigation paths
- Empty world - Use `world:=""` for empty world

**Specify a different world:**
```bash
# Use empty world
ros2 launch robot_description turtlebot3_simulation.launch.py world:=""

# Use custom world file
ros2 launch robot_description turtlebot3_simulation.launch.py world:=/path/to/your/world.sdf
```

**Spawn position:**
You can also specify the robot's initial position:
```bash
ros2 launch robot_description turtlebot3_simulation.launch.py x_pose:=2.0 y_pose:=2.0
```

### Launch Navigation Stack

To use Nav2 navigation stack with TurtleBot3:

```bash
# Terminal 1: Launch simulation
ros2 launch robot_description turtlebot3_simulation.launch.py

# Terminal 2: Launch navigation
ros2 launch robot_description turtlebot3_navigation.launch.py
```

### Run Custom Navigation Node

Run the custom navigation node:
```bash
ros2 run turtlebot3_navigation navigation_node
```

### Run Path Planning Node

Run the path planning node:
```bash
ros2 run turtlebot3_path_planning path_planner_node
```

## Packages

### robot_description
Contains launch files for TurtleBot3 simulation and navigation, plus the warehouse world.

**Launch files:**
- `turtlebot3_simulation.launch.py` - Wrapper that launches TurtleBot3 with Ignition Gazebo
- `turtlebot3_gz_sim.launch.py` - Main launch file using ros_gz_sim (Ignition Gazebo)
  - Spawns TurtleBot3 in the specified world
  - Sets up robot state publisher
  - Bridges cmd_vel topic for robot control
  - Configurable spawn position and world file
- `turtlebot3_navigation.launch.py` - Launches Nav2 navigation stack

**World files:**
- `warehouse.sdf` - Custom warehouse environment (default world)

### turtlebot3_navigation
Custom navigation package with a simple navigation node that:
- Subscribes to goal poses (`/goal_pose`)
- Publishes velocity commands (`/cmd_vel`)
- Uses odometry (`/odom`) for position feedback

### turtlebot3_path_planning
Path planning package with a path planner node that:
- Subscribes to goal poses (`/goal_pose`)
- Subscribes to map data (`/map`)
- Publishes planned paths (`/planned_path`)
- Visualizes paths as markers

## Testing

### Send a Goal Pose

You can send a goal pose using:
```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}"
```

### Teleop Control

For manual control:
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

## Troubleshooting

1. **TurtleBot3 packages not found**: 
   - Make sure you've installed TurtleBot3 from source and sourced the workspace
   - Verify with: `ros2 pkg list | grep turtlebot3`

2. **Gazebo not launching**: 
   - Check that `ros-humble-ros-gz-sim` is installed: `ros2 pkg list | grep ros_gz_sim`
   - Verify Gazebo Sim is installed: `gz sim --version`
   - Note: We use `ros_gz_sim` (Ignition Gazebo) instead of the old `turtlebot3_gazebo` package

3. **TF errors**: 
   - Ensure the robot is spawned and odometry is being published
   - Check TF tree: `ros2 run tf2_tools view_frames`

4. **Navigation not working**: 
   - Check that the map server is running and providing map data
   - Verify Nav2 packages are installed: `ros2 pkg list | grep nav2`

5. **Package not found errors**:
   - Make sure to source both TurtleBot3 workspace and this workspace:
     ```bash
     source ~/turtlebot3_ws/install/setup.bash
     source ~/Workspace/ros2_robot/install/setup.bash
     ```

6. **404 errors during dependency installation**:
   - Some ROS packages may return 404 errors on arm64 architecture (packages not available)
   - This is expected and won't prevent the build from succeeding
   - The installation script skips packages that require unavailable dependencies
   - For simulation, you don't need the hardware-related packages that fail

7. **dynamixel_sdk not found**:
   - This is expected - `dynamixel_sdk` is not available via apt for arm64
   - Packages requiring it (`turtlebot3_node`, etc.) are automatically skipped
   - These packages are only needed for real hardware, not simulation

## License

MIT
