# caddy_ai2_ros2_sim

**ROS 2:** Jazzy | **Simulador:** Gazebo Harmonic | **Proyecto:** CERVAREC

Paquete de integración para el carrito de golf eléctrico **Caddy AI2**, plataforma de pruebas de vehículos, en simulación. Es el punto de entrada único: contiene el launch principal y agrupa como submódulos git todos los paquetes necesarios para lanzar la simulación completa.

---

## Paquetes incluidos (submódulos)

| Submódulo | Rama | Rol |
|---|---|---|
| `caddy_ai2_ros2_description` | `jazzy` | URDF del robot, parámetros físicos, meshes |
| `caddy_ai2_ros2_gazebo_simulation` | `jazzy` | Gazebo Harmonic: mundos, sensores, bridge, RViz |
| `caddy_ai2_ros2_sensors_ydlidar_x4` | `jazzy` | Driver + fragmento URDF del YDLidar X4 |
| `caddy_ai2_ros2_sensors_lidar_sick_lms_291` | `jazzy` | Driver + fragmento URDF del SICK LMS291 |
| `caddy_ai2_ros2_control_sensors_sbg_ig_500n` | `jazzy` | Driver + fragmento URDF de la IMU SBG IG-500N |
| `caddy_ai2_ros2_camera_zed_2i` | `main` | Cámaras ZED 2i: fragmento URDF + sensor Gazebo `rgbd_camera` + launch de `zed-ros2-wrapper` |
| `caddy_ai2_ros2_bicycle_to_ackermann_steering_adapter` | `jazzy` | Controlador ros2_control — conversión dirección |
| `caddy_ai2_ros2_bicycle_to_ackermann_traction_adapter` | `jazzy` | Controlador ros2_control — conversión tracción |
| `caddy_ai2_ros2_robot_description_publisher` | `jazzy` | Publica URDF como topic transient-local |
| `caddy_ai2_ros2_localization` | `main` | EKF (robot_localization): fusión odometría + IMU |
| `caddy_ai2_ros2_navigation` | `main` | EasyNav: SLAM (slam_toolbox), AMCL, A*, Regulated Pure Pursuit (Ackermann) |
| `caddy_ai2_ros2_mvsim_simulation` | `jazzy` | Simulación alternativa con MVSim (planta baja del parking, física 2D), generada desde `robot_params.yaml` |
| `mvsim` | `2.0.0` (etiqueta) | [MVSim](https://github.com/MRPT/mvsim) de MRPT, sin modificar. La 2.0.0 aún no está en `apt` (ahí hay la 1.5.0); se compila con colcon junto al resto |

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
  caddy_ai2_ros2_camera_zed_2i \
  caddy_ai2_ros2_bicycle_to_ackermann_steering_adapter \
  caddy_ai2_ros2_bicycle_to_ackermann_traction_adapter \
  caddy_ai2_ros2_robot_description_publisher \
  caddy_ai2_ros2_localization \
  caddy_ai2_ros2_navigation \
  caddy_ai2_ros2_sim
source install/setup.bash
```

---

## Uso

### Simulación por defecto (world plano)

```bash
ros2 launch caddy_ai2_ros2_sim sim.launch.py
```

### Argumentos disponibles

`sim.launch.py` es el único launch del paquete `caddy_ai2_ros2_sim`.

| Argumento | Default | Descripción |
|---|---|---|
| `world` | `caddy_ai2_world.sdf` | Mundo SDF de `caddy_ai2_ros2_gazebo_simulation/description/world` (relativo) o ruta absoluta |
| `robot_name` | `caddy_ai2` | Nombre del modelo en Gazebo |
| `namespace` | `caddy_ai2` | Namespace ROS 2 |
| `prefix` | `` | Prefijo de TF frames |
| `x`, `y`, `z` | `0.0` | Posición de spawn (m). En el parking, (0, 0) es la planta baja |
| `yaw` | `0.0` | Orientación de spawn (rad) |
| `use_localization` | `true` | EKF (`odom → base_footprint`). EasyNav lo necesita |
| `use_rviz` | `true` | Abre RViz (se ignora con `headless:=true`) |
| `headless` | `false` | Solo servidor de Gazebo, renderizado EGL, sin GUI ni pantalla |
| `nav` | `none` | EasyNav: `none`, `2d` (costmap) o `3d` (NavMap + Helios) |
| `remote_viz` | `false` | Publica la nube del Helios submuestreada para un RViz remoto |

```bash
# Parking de 3 plantas con navegación 3D en un servidor sin pantalla
ros2 launch caddy_ai2_ros2_sim sim.launch.py world:=parking_garage.sdf headless:=true nav:=3d
```

Vídeos de demostración desde Gazebo sin GUI: ver [`tools/`](src/caddy_ai2_ros2_sim/tools/README.md).

### SLAM (construir mapa con el robot)

```bash
# Instalar twist_stamper si aún no está:
sudo apt install ros-jazzy-twist-stamper

ros2 launch caddy_ai2_ros2_navigation slam.launch.py
# Teleoperar y guardar el mapa cuando esté completo:
ros2 service call /caddy_ai2/slam_toolbox/save_map \
  slam_toolbox/srv/SaveMap "{name: {data: 'maps/caddy_ai2_world'}}"
```

### Navegación autónoma (EasyNav)

```bash
# Con el mapa por defecto (maps/navigation_test.yaml del paquete de navegación):
ros2 launch caddy_ai2_ros2_navigation navigation.launch.py

# Con otro mapa (ruta relativa al share de un paquete):
ros2 launch caddy_ai2_ros2_navigation navigation.launch.py \
  map_package:=my_maps_pkg map_file:=maps/my_map.yaml
```

### Cámaras ZED 2i (estudio de disposición)

Hay dos disposiciones definidas en `caddy_ai2_ros2_description/bringup/config/robot_params.yaml`.
Se activa **una sola** con `enabled: true` (la otra pareja en `false`) y se vuelve a lanzar la simulación:

| Disposición | Cámaras | Cobertura horizontal |
|---|---|---|
| A (por defecto) | `zed_2i_left`, `zed_2i_right`: delanteras, en los extremos, yaw ±40° hacia fuera | 190°, con 30° de solape central |
| B | `zed_2i_front`, `zed_2i_rear`: centradas, una delante y otra detrás | 2 × 110°, sin solape; 2 × 70° ciegos en los laterales |

Topics por cámara: `/<namespace>/<cámara>/zed_node/left/color/rect/image`, `.../depth/depth_registered`
y `.../point_cloud/cloud_registered`. Las poses son provisionales hasta medir la barra superior.

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
[Teleop / EasyNav / Planner]
        │  /bicycle_steering_controller/reference  (TwistStamped)
        ▼
[bicycle_to_ackermann_steering_adapter]   [bicycle_to_ackermann_traction_adapter]
        │  steering joints/position              │  drive joints/velocity
        ▼                                        ▼
        └──────── gz_ros2_control (GazeboSimSystem) ──────────┘
                       │  /joint_states            │  /bicycle_steering_controller/odometry
                       ▼                           ▼
          [robot_state_publisher]          [ekf_filter_node]  (use_localization=true)
             /tf (joints)                    /tf  odom → base_footprint
                       │                           │
                       └───────────────────────────┘
                                       ▼
                                    [RViz2]
            ┌──────────────────────────┐
            │  Gazebo Harmonic          │
            │  ├─ IMU SBG IG-500N       │
            │  ├─ SICK LMS291, YDLidar X4
            │  ├─ NavSat (×3): base/CG, front_axle, rear_axle
            │  └─ OdometryPublisher (ground truth 50 Hz)
            └──────────────────────────┘
                       │  ros_gz_bridge
                       ▼
        /sbg_ig500n/imu
        /sick_lms_291/scan, /ydlidar_x4/scan
        /sbg_ig500n/navsat
        /sbg_ig500n/navsat/base/fix  (frame: cg_link)
        /sbg_ig500n/navsat/front_axle/fix, /sbg_ig500n/navsat/rear_axle/fix
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
