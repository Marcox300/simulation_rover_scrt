from os.path import join
from os import environ, pathsep

from ament_index_python.packages import get_package_share_directory, get_package_prefix

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription, OpaqueFunction
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from moveit_configs_utils import MoveItConfigsBuilder


def start_gzserver(context, *args, **kwargs):

    # obtiene el mundo a cargar
    pkg_path = get_package_share_directory('urjc_excavation_world')

    world_name = LaunchConfiguration('world_name').perform(context)
    world = join(pkg_path, 'worlds', world_name + '.world')

    # lanza el servidor de gazebo
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r -s -v 4 ', world]}.items()
    )

    # lanza el cliente grafico de gazebo
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': [' -g ']}.items(),
    )

    return [start_gazebo_server_cmd, start_gazebo_client_cmd]


def get_model_paths(packages_names):

    # construye las rutas de modelos para gazebo
    model_paths = ""

    for package_name in packages_names:

        if model_paths != "":
            model_paths += pathsep

        package_path = get_package_prefix(package_name)
        model_path = join(package_path, "share")
        model_paths += model_path

    if 'GZ_SIM_RESOURCE_PATH' in environ:
        model_paths += pathsep + environ['GZ_SIM_RESOURCE_PATH']

    return model_paths

def generate_launch_description():

    # configuracion de moveit (no se usa directamente pero se incluye como en el ejemplo)
    moveit_config = MoveItConfigsBuilder(
        "rover",
        package_name="rover_scrt_moveit_config"
    ).to_moveit_configs()

    # argumento para usar tiempo de simulacion
    declare_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description="use_sim_time simulation parameter"
    )

    # construccion de rutas de modelos
    model_path = ''
    resource_path = ''

    pkg_path = get_package_share_directory('rover_description')

    model_path += join(pkg_path, 'models')
    resource_path += pkg_path + model_path

    if 'GZ_SIM_MODEL_PATH' in environ:
        model_path += pathsep + environ['GZ_SIM_MODEL_PATH']

    if 'GZ_SIM_RESOURCE_PATH' in environ:
        resource_path += pathsep + environ['GZ_SIM_RESOURCE_PATH']

    model_path = get_model_paths(['rover_description'])

    # lanzamiento de gazebo (server y client)
    start_gazebo_server_cmd = OpaqueFunction(function=start_gzserver)

    # spawn del robot en gazebo
    gazebo_spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-model", "rover_scrt",
            "-topic", "robot_description",
            "-use_sim_time", "True",
        ],
    )

    # lanzamiento del robot state publisher desde moveit
    robot_description_launcher = IncludeLaunchDescription(
        PathJoinSubstitution(
            [FindPackageShare("rover_scrt_moveit_config"), "launch", "rsp.launch.py"]
        ),
    )

    # configuracion de rviz
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("rover_description"), "rviz", "robot.rviz"]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )

    # bridge entre gazebo y ros2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_ros_gz',
        parameters=[
            {
                'config_file': join(pkg_path, 'config', 'rover_bridge.yaml'),
                'use_sim_time': True,
            }
        ],
        output='screen',
    )

    # bridge para imagenes de camaras
    gz_image_bridge_node = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=[
            "/front_camera/image",
            "/arm_camera/image"
        ],
        output="screen",
        parameters=[
            {
                'use_sim_time': True,
                'camera.image.compressed.jpeg_quality': 75
            }
        ],
    )

    # nodo para añadir timestamp a cmd_vel
    twist_stamped = Node(
        package="twist_stamper",
        executable="twist_stamper",
        name="twist_stamper",
        output="screen",
        parameters=[
            {
                "use_sim_time": True
            }
        ],
        remappings={
            ('cmd_vel_out', '/rover_base_control/cmd_vel'),
            ('cmd_vel_in', '/cmd_vel')
        },
    )

    # creacion del launch description
    ld = LaunchDescription()

    ld.add_action(SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', model_path))
    ld.add_action(SetEnvironmentVariable('GZ_SIM_MODEL_PATH', model_path))

    ld.add_action(robot_description_launcher)
    ld.add_action(declare_sim_time)

    ld.add_action(bridge)
    ld.add_action(gz_image_bridge_node)

    ld.add_action(start_gazebo_server_cmd)

    ld.add_action(rviz_node)
    ld.add_action(gazebo_spawn_robot)

    ld.add_action(twist_stamped)

    return ld
