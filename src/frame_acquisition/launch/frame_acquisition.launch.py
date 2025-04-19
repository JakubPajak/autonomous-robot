from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    # Camera parameters
    camera_fps = DeclareLaunchArgument(
        "camera_fps", default_value="30",
        description="Frames per second for the camera."
    )

    return LaunchDescription([
        camera_fps,


        Node(
            package='frame_acquisition',
            executable='acquire_frame',
            name='acquire_frame',
            # parameters=[{"camera_fps": LaunchConfiguration("camera_fps")}]
        ),

        Node(
            package='frame_acquisition',
            executable='process_frame',
            name='process_frame'
        ),

        Node(
            package='frame_acquisition',
            executable='process_frame_bin',
            name='process_frame_bin'
        ),

        # Foxglove Bridge for visualization
        Node(
            package="foxglove_bridge",
            executable="foxglove_bridge",
            name="foxglove_bridge",
            output="screen",
            parameters=[{"port": 8765}]  # Default WebSocket port for Foxglove
        ),
    ])
