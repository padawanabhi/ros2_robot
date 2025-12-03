from setuptools import find_packages, setup

package_name = 'turtlebot3_path_planning'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abhishek',
    maintainer_email='abhishek.nair123@yahoo.com',
    description='Path planning package for TurtleBot3',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'path_planner_node = turtlebot3_path_planning.path_planner_node:main',
        ],
    },
)
