import numpy as np
import matplotlib.pyplot as plt
import sys

from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message

from sensor_msgs.msg import JointState, Imu


# comprobar entrada
if len(sys.argv) < 2:
    print("uso: python3 plot_rosbag.py <ruta_rosbag>")
    exit()

bag_path = sys.argv[1]

# abrir rosbag mcap
reader = SequentialReader()

storage_options = StorageOptions(
    uri=bag_path,
    storage_id='mcap'
)

converter_options = ConverterOptions(
    input_serialization_format='cdr',
    output_serialization_format='cdr'
)

reader.open(storage_options, converter_options)

# estructuras de datos
t_joint = []
t_imu = []

wheel_data = {}
scara_data = {}
gripper_data = {}

effort_data = {}

imu_acc = []

# tiempo base
t0 = None

# leer rosbag
while reader.has_next():

    topic, data, t = reader.read_next()

    t = t * 1e-9

    if t0 is None:
        t0 = t

    t = t - t0

    # joint states
    if topic == "/joint_states":

        msg = deserialize_message(data, JointState)

        t_joint.append(t)

        for i, name in enumerate(msg.name):

            pos = msg.position[i]
            eff = abs(msg.effort[i])

            # ruedas
            if "wheel" in name or "rueda" in name:

                if name not in wheel_data:
                    wheel_data[name] = []

                wheel_data[name].append(pos)

            # brazo scara
            elif (
                ("joint" in name or "scara" in name)
                and "pinza" not in name
                and "gripper" not in name
                and "wheel" not in name
                and "rueda" not in name
            ):

                if name not in scara_data:
                    scara_data[name] = []

                scara_data[name].append(pos)

            # gripper
            if "pinza" in name or "gripper" in name:

                if name not in gripper_data:
                    gripper_data[name] = []

                gripper_data[name].append(pos)

            # esfuerzos
            if name not in effort_data:
                effort_data[name] = []

            effort_data[name].append(eff)

    # imu
    elif topic == "/imu":

        msg = deserialize_message(data, Imu)

        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z

        acc = np.sqrt(ax**2 + ay**2 + az**2)

        imu_acc.append(acc)
        t_imu.append(t)

# calcular gasto total solo del pick and place
G = []

pick_effort_data = {}

for name, values in effort_data.items():

    if (
        ("joint" in name or "scara" in name or "pinza" in name or "gripper" in name)
        and "wheel" not in name
        and "rueda" not in name
    ):
        pick_effort_data[name] = values

min_len = min([len(v) for v in pick_effort_data.values()]) if pick_effort_data else 0

for i in range(min_len):

    total = 0

    for name in pick_effort_data:

        if i < len(pick_effort_data[name]):
            total += pick_effort_data[name][i]

    G.append(total)

t_g = t_joint[:len(G)]

# figura 1 ruedas
plt.figure()

for name, values in wheel_data.items():

    n = min(len(t_joint), len(values))

    plt.plot(t_joint[:n], values[:n], label=name)

plt.title("posicion ruedas vs tiempo")
plt.xlabel("tiempo (s)")
plt.ylabel("posicion (rad)")
plt.grid()
plt.legend()

# figura 2 scara + gripper posiciones
plt.figure()

for name, values in scara_data.items():

    n = min(len(t_joint), len(values))

    plt.plot(t_joint[:n], values[:n], label=name)

for name, values in gripper_data.items():

    n = min(len(t_joint), len(values))

    plt.plot(t_joint[:n], values[:n], linestyle='--', label=name)

plt.title("joints scara y gripper vs tiempo")
plt.xlabel("tiempo (s)")
plt.ylabel("posicion")
plt.grid()
plt.legend()

# figura 3 imu
plt.figure()

plt.plot(t_imu, imu_acc)

plt.title("aceleracion vs tiempo")
plt.xlabel("tiempo (s)")
plt.ylabel("aceleracion (m/s^2)")
plt.grid()

# figura 4 gasto total pick and place
plt.figure()

plt.plot(t_g, G)

plt.title("gasto del mecanismo pick and place")
plt.xlabel("tiempo (s)")
plt.ylabel("g_parcial")
plt.grid()

# figura 5 fuerzas individuales scara + gripper
plt.figure()

for name, values in pick_effort_data.items():

    n = min(len(t_joint), len(values))

    if "pinza" in name or "gripper" in name:
        plt.plot(t_joint[:n], values[:n], linestyle='--', label=name)

    else:
        plt.plot(t_joint[:n], values[:n], label=name)

plt.title("fuerzas individuales scara y gripper")
plt.xlabel("tiempo (s)")
plt.ylabel("fuerza / esfuerzo")
plt.grid()
plt.legend()

# estadisticas
print("estadisticas gasto")

if len(G) > 0:

    print("media:", np.mean(G))
    print("max:", np.max(G))
    print("std:", np.std(G))
    print("total:", np.sum(G))

else:
    print("no hay datos de esfuerzo")

plt.show()