# Simulation_rover_scrt
# Práctica 3 - Modelado y Simulación de Robots (GIRS)

## 1. Lanzamiento del sistema y información del proyecto

Para ejecutar correctamente la simulación del robot se deben lanzar los siguientes componentes en terminales separadas:

- Lanzamiento del mundo y robot en Gazebo

```bash
ros2 launch rover_description robot_gazebo.launch.py world_name:=urjc_excavation_msr
```

- Lanzamiento de MoveIt
```bash
ros2 launch rover_scrt_moveit_config move_group.launch.py
```

- Lanzamiento de controladores y Teleoperación de la base
```bash
ros2 launch rover_description robot_controllers.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Para obtener información de las TF se ha generado el árbol de transformadas:

[Árbol de transformadas (TF)](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/data/tf.pdf)

Además se puede lanzar:
```bash
ros2 launch rover_description  robot_launch.launch.py
```
De esta forma podemos analizar en RViz2 los datos del urdf.
Obteniendo:

![pose1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rviz_1a.png)
![pose1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rviz_1b.png)
![pose2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rviz_2a.png)
![pose2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rviz_2b.png)

## 2. Comportamiento del robot durante la teleoperación

En esta sección se describe el comportamiento general del robot durante la ejecución de la tarea de pick and place y desplazamiento.

El robot realiza las siguientes acciones:
- Recogida del cubo verde situado frente al robot
- Transporte y colocación del cubo azul sobre el cubo rojo
- Movimiento final en línea recta

Durante estas fases se observan variaciones en:
- Velocidad de la base (/cmd_vel)
- Esfuerzo en las articulaciones del brazo SCARA
- Apertura y cierre del gripper
- Variaciones en la aceleración medida por la IMU

---

## 3. Análisis de datos obtenidos

En esta sección se presentan las gráficas obtenidas a partir del rosbag con los topics:
- /cmd_vel
- /joint_states
- /imu

Tener en cuenta que en la carpeta [rosbag](https://github.com/Marcox300/simulation_rover_scrt/tree/main/rosbag) se encuentran dos rosbag.
En el primero se completan los objetivos de colocación del robot, pero la IMU no se estaba publicando debido a un error en un archivo `.yaml`.
En el segundo, la IMU sí se registra correctamente, aunque el cubo azul se cayó justo antes de abrir las pinzas; aun así, se simuló la apertura correspondiente del gripper.

Por este motivo, se analizarán ambos resultados, ya que en el primer rosbag se realizan varios movimientos de giro con el rover,
mientras que en el segundo se mantiene lo más estático posible y únicamente se mueve el SCARA.

### 3.1 Posición de las ruedas

---

### 3.2 Aceleración de la IMU


---

### 3.3 Gasto del mecanismo pick and place


### 3.4 Fuerzas y posiciones del pick an place


---

## 4. Enlaces de interés

### Repositorio del proyecto
https://github.com/Marcox300/simulation_rover_scrt/tree/main

### Repositorio de pruebas en Gazebo
https://github.com/juanscelyg/urjc-excavation-world


---

## 5. Capturas de simulación

### Robot cubo verde

### Robot cubo azul


---

## 6. Conclusiones

