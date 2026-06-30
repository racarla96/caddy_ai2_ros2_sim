# caddy_ai2_ros2_sim

**ROS 2:** Jazzy | **Simulador:** Gazebo Harmonic | **Proyecto:** CERVAREC

Paquete de integración para el robot agrícola **Caddy AI2** en simulación. Es el punto de entrada único: contiene el launch principal y agrupa como submódulos git todos los paquetes necesarios para lanzar la simulación completa.

---

## Paquetes incluidos (submódulos)

| Submódulo | Rama | Rol |
|---|---|---|
| `caddy_ai2_ros2_description` | `jazzy` | URDF del robot, parámetros físicos, meshes |
| `caddy_ai2_ros2_gazebo_simulation` | `jazzy` | Gazebo Harmonic: mundos, sensores, bridge, RViz |
| `caddy_ai2_ros2_sensors_ydlidar_x4` | `jazzy` | Driver + fragmento URDF del YDLidar X4 |
| `caddy_ai2_ros2_sensors_lidar_sick_lms_291` | `jazzy` | Driver + fragmento URDF del SICK LMS291 |
| `caddy_ai2_ros2_control_sensors_sbg_ig_500n` | `jazzy` | Driver + fragmento URDF de la IMU SBG IG-500N |
| `caddy_ai2_ros2_bicycle_to_ackermann_steering_adapter` | `jazzy` | Controlador ros2_control — conversión dirección |
| `caddy_ai2_ros2_bicycle_to_ackermann_traction_adapter` | `jazzy` | Controlador ros2_control — conversión tracción |
| `caddy_ai2_ros2_robot_description_publisher` | `jazzy` | Publica URDF como topic transient-local |
| `caddy_ai2_ros2_localization` | `main` | EKF (robot_localization): fusión odometría + IMU |

---

## Instalación

### 1. Clonar como workspace

Este repo ES el workspace — se clona directamente en la carpeta raíz, no dentro de `src/`:

```bash
git clone --recurse-submodules -b jazzy \
  https://github.com/racarla96/caddy_ai2_ros2_sim.git ~/caddy_ws
```

Si ya tienes el repo clonado sin submódulos:

```bash
cd ~/caddy_ws
git submodule update --init --recursive
```

### 3. Instalar dependencias del sistema

```bash
# ROS 2 control
sudo apt install ros-jazzy-ros2-control ros-jazzy-ros2-controllers

# Gazebo Harmonic + bridge
sudo apt install ros-jazzy-gz-ros2-control ros-jazzy-ros-gz-bridge \
                 ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-interfaces

# Visualización
sudo apt install ros-jazzy-robot-state-publisher ros-jazzy-rviz2

# Python (templates Jinja2)
pip install jinja2 pyyaml
```

### 4. Compilar

```bash
cd ~/caddy_ws
colcon build --packages-select \
  caddy_ai2_ros2_description \
  caddy_ai2_ros2_gazebo_simulation \
  caddy_ai2_ros2_sensors_ydlidar_x4 \
  caddy_ai2_ros2_sensors_lidar_sick_lms_291 \
  caddy_ai2_ros2_control_sensors_sbg_ig_500n \
  caddy_ai2_ros2_bicycle_to_ackermann_steering_adapter \
  caddy_ai2_ros2_bicycle_to_ackermann_traction_adapter \
  caddy_ai2_ros2_robot_description_publisher \
  caddy_ai2_ros2_localization \
  caddy_ai2_ros2_sim
source install/setup.bash
```

---

## Uso

### Simulación por defecto (world plano)

```bash
ros2 launch caddy_ai2_ros2_sim sim_gazebo.launch.py
```

### Argumentos disponibles

| Argumento | Default | Descripción |
|---|---|---|
| `world` | `caddy_ai2_world.sdf` | Fichero SDF (relativo) o ruta absoluta |
| `robot_name` | `caddy_ai2` | Nombre del modelo en Gazebo |
| `namespace` | `` | Namespace ROS 2 |
| `prefix` | `` | Prefijo de TF frames |
| `x`, `y`, `z` | `0.0` | Posición de spawn (m) |
| `yaw` | `0.0` | Orientación de spawn (rad) |
| `use_localization` | `true` | Lanza el nodo EKF (robot_localization) |

### Control manual

```bash
ros2 topic pub /bicycle_steering_controller/reference geometry_msgs/msg/TwistStamped "{
  header: {frame_id: 'base_link'},
  twist: {linear: {x: 1.0}, angular: {z: 0.3}}
}"
```

---

## Arquitectura del sistema

```
[Teleop / Nav2 / Planner]
        │  /bicycle_steering_controller/reference  (TwistStamped)
        ▼
[bicycle_to_ackermann_steering_adapter]   [bicycle_to_ackermann_traction_adapter]
        │  steering joints/position              │  drive joints/velocity
        ▼                                        ▼
        └──────── gz_ros2_control (GazeboSimSystem) ──────────┘
                       │  /joint_states
                       ▼
          [robot_state_publisher]  →  /tf  →  [RViz2]
                       │
            ┌──────────────────────────┐
            │  Gazebo Harmonic          │
            │  ├─ Sensors: IMU, LIDARs, NavSat (×3), GPS
            │  └─ OdometryPublisher (ground truth 50 Hz)
            └──────────────────────────┘
                       │  ros_gz_bridge
                       ▼
        /imu, /sick_lms_291/scan, /ydlidar_x4/scan
        /navsat, /navsat/base/fix, /navsat/front_axle/fix, /navsat/rear_axle/fix
        /ground_truth/odometry
```

---

## Actualizar submódulos al último commit de cada rama

```bash
git submodule update --remote --merge
git add .
git commit -m "Update submodules to latest"
```

---

## Licencia

Copyright (c) 2026, Rafael Carbonell Lázaro (racarla96) — CC BY 4.0
