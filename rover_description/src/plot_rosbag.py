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

# inicializar estructuras de datos
t_joint = []
t_imu = []

wheel_data = {}
effort_data = {}

imu_acc = []

# leer rosbag
while reader.has_next():
    topic, data, t = reader.read_next()

    t = t * 1e-9

    # joint states
    if topic == "/joint_states":
        msg = deserialize_message(data, JointState)

        t_joint.append(t)

        for i, name in enumerate(msg.name):

            # ruedas
            if "wheel" in name or "rueda" in name:
                if name not in wheel_data:
                    wheel_data[name] = []
                wheel_data[name].append(msg.position[i])

            # esfuerzo
            if name not in effort_data:
                effort_data[name] = []
            effort_data[name].append(abs(msg.effort[i]))

    # imu
    elif topic == "/imu/data":
        msg = deserialize_message(data, Imu)

        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z

        imu_acc.append(np.sqrt(ax**2 + ay**2 + az**2))
        t_imu.append(t)

# calcular gasto total
G = []

min_len = min([len(v) for v in effort_data.values()]) if effort_data else 0

for i in range(min_len):
    total = 0
    for name in effort_data:
        if i < len(effort_data[name]):
            total += effort_data[name][i]
    G.append(total)

t_g = t_joint[:len(G)]

# plot ruedas
plt.figure()

for name, values in wheel_data.items():
    n = min(len(t_joint), len(values))
    plt.plot(t_joint[:n], values[:n], label=name)

plt.title("posición de ruedas vs tiempo")
plt.xlabel("tiempo (s)")
plt.ylabel("posición (rad)")
plt.grid()
plt.legend()

# plot imu
plt.figure()
plt.plot(t_imu, imu_acc)

plt.title("aceleración vs tiempo")
plt.xlabel("tiempo (s)")
plt.ylabel("aceleración (m/s^2)")
plt.grid()

# plot gasto
plt.figure()
plt.plot(t_g, G)

plt.title("gasto del mecanismo pick and place")
plt.xlabel("tiempo (s)")
plt.ylabel("g_parcial")
plt.grid()

# estadisticas
print("estadísticas gasto")

if len(G) > 0:
    print("media:", np.mean(G))
    print("max:", np.max(G))
    print("std:", np.std(G))
    print("total:", np.sum(G))
else:
    print("no hay datos de esfuerzo")

plt.show()