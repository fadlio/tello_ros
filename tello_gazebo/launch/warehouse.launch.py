import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')

    world_path = os.path.join(get_package_share_directory('tello_gazebo'),
                              'worlds', 'no_roof_small_warehouse.world')
    launch_file_dir = os.path.join(
        get_package_share_directory('tello_gazebo'), 'launch')

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    urdf_path = os.path.join(
        get_package_share_directory('tello_description'),
        'urdf',
        'tello.urdf')

    rviz_path = os.path.join(
        get_package_share_directory('tello_gazebo'), 'rviz', 'main.rviz')

    return LaunchDescription([
        # Gazebo envs
        SetEnvironmentVariable(name='GAZEBO_RESOURCE_PATH', value=[
                               '/usr/share/gazebo-11']),

        # Gazebo Server
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
            ),
            launch_arguments={'world': world_path}.items(),
        ),

        # Gazebo Client
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
            ),
        ),

        # Spawn urdf
        Node(package='gazebo_ros', executable='spawn_entity.py',
             arguments=['-entity', 'tello', '-file', urdf_path, '-z', '1']
             ),

        # Robot State Publisher
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [launch_file_dir, '/robot_state_publisher.launch.py']),
            launch_arguments={'use_sim_time': use_sim_time}.items(),
        ),

        # Tello Driver
        Node(package='tello_driver',
             executable='tello_joy_main', namespace="drone"
             ),

        # Joystick
        Node(package='joy', executable='joy_node', namespace="drone"),

        # RViz2
        Node(
            package='rviz2', executable='rviz2', name='rviz2',
            arguments=['-d', rviz_path]
        ),
    ])
