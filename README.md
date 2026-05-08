# Simulation_rover_scrt
# Práctica 3 - Modelado y Simulación de Robots

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

En esta sección se analiza la evolución de la posición de las ruedas del rover durante la teleoperación.

Se comparan dos experimentos:
- Rosbag 1: el robot realiza giros y maniobras continuas.
- Rosbag 2: el robot permanece prácticamente estático, con movimiento mínimo de la base hacia atras para acercarse a los cubos.

Esto permite observar que en el primer caso existe una mayor variación en las posiciones de las ruedas debido a los cambios de dirección.
Asimismo, se aprecia que las ruedas se desplazan en sentidos opuestos, lo que refleja la simetría propia de los giros holonómicos del sistema (rosbag1).

- Rosbag 1  
![ruedas_rosbag1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/plot_ruedas.png)

- Rosbag 2  
![ruedas_rosbag2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/plot_ruedas.png)

---

### 3.2 Aceleración de la IMU

En este apartado se analiza la aceleración medida por la IMU, que refleja el movimiento del chasis del robot.

- En rosbag 1 no se aprecia nada al no existir publicación de la imu por el error mencionado al inicio.
- En rosbag 2 la señal es más estable al mantenerse el robot prácticamente estático.
hay que tener en cuenta que en la generación del plot usamos la magnitud de la aceleración:
```python3
acc = np.sqrt(ax**2 + ay**2 + az**2)
```
y que en gazebo se simula la gravedad. es por eso que, si solo queremos tener como referencia las aceleraciones del plano de movimiento,
debemos ignorar la componente en z, ya que está dominada por la gravedad. esto permite eliminar el efecto dominante de la gravedad en la medida,
aunque también reduce parcialmente la capacidad de detectar pequeñas variaciones debidas a irregularidades del entorno o contactos del sistema.

- Rosbag 1  
![imu_rosbag1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/plot_imu.png)

- Rosbag 2  
![imu_rosbag2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/plot_imu.png)

---

### 3.3 Gasto del mecanismo pick and place

se representa el gasto energético (G_parcial) del sistema, calculado como la suma de los esfuerzos en las articulaciones del scara y el gripper.

- en rosbag 1 el gasto es más irregular debido a un movimiento menos fluido y a ajustes continuos del scara durante la teleoperación.
- en rosbag 2 el gasto se concentra en las fases de manipulación del scara sin exceso de movimientos, lo que indica una ejecución más estable.

en esta parte es difícil apreciar con claridad en qué momento se ejecutan los movimientos, por lo que se ha añadido el apartado 3.4, donde se pueden distinguir mejor las fases del proceso.

en cualquier caso, el movimiento se divide en:

1. agarrar el cubo verde  
2. guardar el cubo verde  
3. agarrar el cubo azul  
4. depositar el cubo azul sobre el rojo

- Rosbag 1  
![gasto_rosbag1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/plot_gasto.png)

- Rosbag 2  
![gasto_rosbag2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/plot_gasto.png)

---

### 3.4 Fuerzas y posiciones del pick and place

En esta sección se comparan las posiciones articulares del SCARA y gripper junto con las fuerzas (esfuerzos) en cada articulación.

Se observa que el SCARA concentra la mayor parte del esfuerzo durante la manipulación, mientras que el gripper presenta picos en apertura y cierre.

En ambos rosbag se aprecia que el gripper es el que ejerce mayores esfuerzos relativos durante las fases de agarre, debido a que debe vencer la gravedad y 
sujetar tanto su propio mecanismo como el peso de los cubos. Por su parte, el brazo SCARA también presenta picos de fuerza al tener que mover la carga completa del sistema.

Se debe destacar que en el rosbag 2 aparece un pico de fuerza anómalo en una de las articulaciones del gripper, 
a pesar de que en condiciones normales el sistema está limitado a valores máximos de esfuerzo de 100.
Esto puede deberse a un error puntual de muestreo o a una transición brusca durante la simulación.


- Rosbag 1  
![scara_rosbag1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/plot_scara.png)
![fuerzas_rosbag1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/plot_scara_fuerzas_individuales.png)


- Rosbag 2  
![scara_rosbag2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/plot_scara.png)  
![fuerzas_rosbag2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/plot_scara_fuerzas_individuales.png)



---

## 4. Capturas de simulación

En esta sección se muestran las capturas de la simulación correspondientes a ambos rosbag utilizados en el análisis.

---

### Rosbag 1


![rosbag1_1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/1.png)
![rosbag1_2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/2.png)
![rosbag1_3](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/3.png)
![rosbag1_4](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_1/4.png)

---

### Rosbag 2


![rosbag2_1](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/1.png)
![rosbag2_2](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/2.png)
![rosbag2_3](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/3.png)
![rosbag2_4](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/4.png)
![rosbag2_5](https://github.com/Marcox300/simulation_rover_scrt/blob/main/rover_description/data/img/rosbag_2/5.png)

---

## 5. Conclusiones

Uno de los principales problemas observados en la simulación es la capacidad de agarre del gripper. Se han realizado distintos ajustes en los parámetros de fricción y rozamiento con el objetivo de mejorar la estabilidad del agarre, sin embargo, el problema principal parece derivar de un comportamiento no deseado en el cierre de la pinza.

En particular, durante la fase de cierre, las articulaciones del gripper presentan desplazamientos hacia configuraciones no previstas, lo que provoca inestabilidad en la sujeción de los objetos. Este comportamiento afecta directamente a la fiabilidad de la tarea de pick and place en determinadas ejecuciones. Esto es posiblemente aleatorio poratanto no puedo garantizar que una misma ejecución afecte de la misma manera.

## 6. Enlaces del proyecto

Repositorio principal del proyecto:

https://github.com/Marcox300/simulation_rover_scrt

Entorno de simulación utilizado (Gazebo world):

https://github.com/juanscelyg/urjc-excavation-world
