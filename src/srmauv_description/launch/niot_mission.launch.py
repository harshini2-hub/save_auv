import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('srmauv_description')
    gazebo_ros = get_package_share_directory('gazebo_ros')

    xacro_file = os.path.join(pkg, 'urdf', 'srmauv.urdf.xacro')
    robot_desc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    world = os.path.join(pkg, 'worlds', 'niot_mission.world')

    set_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=os.environ.get('GAZEBO_MODEL_PATH', '') + os.pathsep + os.path.dirname(pkg),
    )

    set_plugin_path = SetEnvironmentVariable(
        name='GAZEBO_PLUGIN_PATH',
        value=os.environ.get('GAZEBO_PLUGIN_PATH', '') + os.pathsep +
              os.path.expanduser('~/save_auv/install/srmauv_dynamics/lib'),
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'verbose': 'true', 'world': world}.items(),
    )

    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros, 'launch', 'gzclient.launch.py')),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        output='screen', parameters=[{'robot_description': robot_desc}],
    )

    spawn = Node(
        package='gazebo_ros', executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'srmauv',
                   '-x', '-11.0', '-y', '0.0', '-z', '1.2', '-Y', '0.0'],
        output='screen',
    )

    return LaunchDescription([
        set_model_path, set_plugin_path, gzserver, gzclient,
        robot_state_publisher, spawn,
    ])
