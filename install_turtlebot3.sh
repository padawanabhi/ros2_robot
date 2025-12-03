#!/bin/bash
# Script to install TurtleBot3 packages in this workspace

# Don't exit on errors - we want to continue even if some dependencies fail
# set -e

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$WORKSPACE_DIR/src"

echo "Installing TurtleBot3 packages in workspace: $WORKSPACE_DIR"

# Check if we're in the right directory
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: src directory not found. Are you in the workspace root?"
    exit 1
fi

cd "$SRC_DIR"

# Clone TurtleBot3 packages if they don't exist
if [ ! -d "turtlebot3" ]; then
    echo "Cloning turtlebot3..."
    git clone https://github.com/ROBOTIS-GIT/turtlebot3.git -b humble
else
    echo "turtlebot3 already exists, skipping..."
fi

if [ ! -d "turtlebot3_msgs" ]; then
    echo "Cloning turtlebot3_msgs..."
    git clone https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git -b humble
else
    echo "turtlebot3_msgs already exists, skipping..."
fi

if [ ! -d "turtlebot3_simulations" ]; then
    echo "Cloning turtlebot3_simulations..."
    git clone https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git -b humble
else
    echo "turtlebot3_simulations already exists, skipping..."
fi

# Install dependencies
echo "Installing dependencies..."
cd "$WORKSPACE_DIR"
rosdep update
rosdep install --from-paths src --ignore-src -r -y || echo "Warning: Some dependencies may need manual installation"

# Build packages (skip packages that require hardware or are incompatible)
echo "Building packages..."
echo "Note: Skipping turtlebot3_gazebo (incompatible with Ignition Gazebo)"
echo "Note: Skipping turtlebot3_node, turtlebot3_example, turtlebot3_fake_node (require hardware dependencies)"
echo "Note: Skipping turtlebot3_simulations and turtlebot3 (metapackages depending on skipped packages)"
colcon build --symlink-install --packages-skip \
    turtlebot3_gazebo \
    turtlebot3_manipulation_gazebo \
    turtlebot3_node \
    turtlebot3_example \
    turtlebot3_fake_node \
    turtlebot3_simulations \
    turtlebot3

echo ""
echo "Installation complete!"
echo ""
echo "To use TurtleBot3, source the workspace:"
echo "  source $WORKSPACE_DIR/install/setup.bash"
echo ""
echo "Set the TurtleBot3 model:"
echo "  export TURTLEBOT3_MODEL=burger"

