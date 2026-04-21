# caddy_ai2_ros2_sim

Paquete de integración para el robot agrícola **Caddy AI2** en **simulación**.  
Este repositorio es el punto de entrada para lanzar el sistema completo en entorno simulado. Orquesta el simulador elegido, el stack de ros2_control con hardware interfaces simulados, los adaptadores cinemáticos y la visualización en RViz.

**ROS 2:** Jazzy | **Simuladores soportados:** Gazebo Harmonic · MVSim | **Proyecto:** CERVAREC

---

## Arquitectura del sistema (simulación)

```
[Nav2 / Planner  ó  Teleop]
        │  /cmd_vel  (geometry_msgs/Twist)
        ▼
[bicycle_to_ackermann_steering_adapter]   [bicycle_to_ackermann_traction_adapter]
        │  /forward_command_controller     │  /velocity_controller
        │  /commands  (Float64MultiArray)  │  /commands  (Float64MultiArray)
        ▼                                  ▼
        └──────── ros2_control (mock / sim HW interface) ───────────┘
                       │  /joint_states
                       ▼
              [robot_state_publisher]  →  [RViz2]
                       │  /tf
                       ▼
            ┌──────────────────────┐
            │  Gazebo Harmonic     │  ó  │  MVSim  │
            │  (gz_ros2_control)   │     │  (mvsim_node) │
            └──────────────────────┘
```

---

## Repositorios dependientes

| Repositorio | Rama | Rol |
|---|---|---|
| `caddy_ai2_ros2_description` | `jazzy` | URDF / meshes del robot |
| `caddy_ai2_ros2_common` | `jazzy` | Launch utils compartidos |
| `caddy_ai2_ros2_bicycle_to_ackermann_steering_adapter` | `jazzy` | Conversión cinemática → steering |
| `caddy_ai2_ros2_bicycle_to_ackermann_traction_adapter` | `jazzy` | Conversión cinemática → traction |
| `caddy_ai2_ros2_gazebo_simulation` | `jazzy` | Mundos y configuración Gazebo |
| `caddy_ai2_ros2_mvsim_simulation` | `jazzy` | Mundos y configuración MVSim |

> Los drivers de hardware real (`_steering_driver`, `_traction_driver`) **no son necesarios** en simulación pura. El URDF activa el plugin `gz_ros2_control` o el mock hardware interface según el simulador.

---

## Política de ramas

| Rama | Propósito |
|---|---|
| `jazzy` | Rama estable. Solo se integra código probado. |
| `feat/<nombre>` | Desarrollo de nuevas funcionalidades. Se abre desde `jazzy` y se integra con PR. Ejemplo: `feat/nav2-integration` |
| `hw/<nombre>` | Pruebas puntuales sobre hardware real que no son una feature completa. Vida corta. Solo aplica a `caddy_ai2_ros2_robot`, pero se documenta aquí para referencia. |

> **Regla general:** nunca se hace commit directo a `jazzy`. Todo entra por PR desde `feat/`.

---

## Instalación

### 1. Crear el workspace y clonar los repos necesarios

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src

# Repos de integración
git clone -b jazzy https://github.com/racarla96/caddy_ai2_ros2_sim.git

# Descripción
git clone -b jazzy https://github.com/racarla96/caddy_ai2_ros2_description.git

# Librería común
git clone -b jazzy https://github.com/racarla96/caddy_ai2_ros2_common.git

# Adaptadores cinemáticos
git clone -b jazzy https://github.com/racarla96/caddy_ai2_ros2_bicycle_to_ackermann_steering_adapter.git
git clone -b jazzy https://github.com/racarla96/caddy_ai2_ros2_bicycle_to_ackermann_traction_adapter.git

# Simuladores (clonar solo los que se vayan a usar)
git clone -b jazzy https://github.com/racarla96/caddy_ai2_ros2_gazebo_simulation.git
git clone -b jazzy https://github.com/racarla96/caddy_ai2_ros2_mvsim_simulation.git
```

### 2. Instalar dependencias del sistema

```bash
# ROS 2 control
sudo apt install ros-jazzy-ros2-control ros-jazzy-ros2-controllers

# Descripción del robot
sudo apt install ros-jazzy-xacro ros-jazzy-robot-state-publisher ros-jazzy-rviz2

# Gazebo Harmonic
sudo apt install ros-jazzy-gz-ros2-control ros-jazzy-ros-gz-bridge

# MVSim
sudo apt install ros-jazzy-mvsim
```

### 3. Compilar

```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Uso

### Lanzar con Gazebo Harmonic

```bash
ros2 launch caddy_ai2_ros2_sim sim_gazebo.launch.py
```

### Lanzar con MVSim

```bash
ros2 launch caddy_ai2_ros2_sim sim_mvsim.launch.py
```

### Argumentos comunes

| Argumento | Default | Descripción |
|---|---|---|
| `use_rviz` | `true` | Lanzar RViz con configuración predefinida |
| `world` | `empty` | Mundo a cargar (vacío, campo, almacén…) |
| `use_nav2` | `false` | Lanzar stack de navegación Nav2 |
| `use_teleop` | `false` | Lanzar control por teclado |

### Teleoperación manual

```bash
# En otra terminal
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Verificar controladores activos

```bash
ros2 control list_controllers
```

---

## TODO

### Rama estable (`jazzy`)

#### Unificación de repositorios
- [ ] Alinear todas las ramas de los repos dependientes a `jazzy`
  - [ ] `caddy_ai2_ros2_description`: está en `jazzy-dev` → renombrar/mergear a `jazzy`
  - [ ] `caddy_ai2_ros2_mvsim_simulation`: está en `main` → migrar a `jazzy`
  - [ ] `caddy_ai2_ros2_gazebo_simulation`: verificar rama actual y alinear a `jazzy`
- [ ] Actualizar el README de `caddy_ai2_ros2_description` para que refleje la estructura multirepo actual
- [ ] Mover los meshes duplicados de `caddy_ai2_ros2_mvsim_simulation/meshes/` a `caddy_ai2_ros2_description/meshes/` y actualizar referencias

#### Launch system
- [ ] Crear `launch/sim_gazebo.launch.py` — launch completo con Gazebo Harmonic
  - [ ] Lanzar el mundo seleccionado por parámetro
  - [ ] Lanzar `robot_state_publisher` con URDF de `_description` + plugin `gz_ros2_control`
  - [ ] Lanzar `controller_manager` con mock/sim hardware interfaces
  - [ ] Lanzar los dos adaptadores bicycle→ackermann
  - [ ] Lanzar RViz (condicional a `use_rviz`)
- [ ] Crear `launch/sim_mvsim.launch.py` — launch completo con MVSim
  - [ ] Integrar el launch existente de `caddy_ai2_ros2_mvsim_simulation`
  - [ ] Unificar interfaz de argumentos con el launch de Gazebo
- [ ] Crear `launch/sim.launch.py` — wrapper que selecciona simulador mediante argumento `simulator:=gazebo|mvsim`

#### Configuración centralizada
- [ ] Crear `config/controllers_sim.yaml` con los controladores para simulación
- [ ] Crear `config/rviz/sim.rviz` con configuración de RViz para simulación
- [ ] Definir al menos dos mundos: vacío y un campo agrícola básico (surcos)

#### Integración con Nav2
- [ ] Definir los parámetros de Nav2 adaptados al modelo cinemático Ackermann del Caddy AI2
- [ ] Añadir `launch/nav2.launch.py` que lanza Nav2 sobre la simulación
- [ ] Verificar la integración del `AckermannDriveController` o del `BicycleSteeringController` de ros2_controllers como alternativa a los adaptadores propios

#### Paridad simulación ↔ hardware real
- [ ] Verificar que los nombres de topics y TF frames son idénticos entre `_sim` y `_robot`
- [ ] Verificar que el URDF usado en simulación y en hardware real es el mismo (un solo fichero en `_description`, sin copias)
- [ ] Añadir test de humo: script que lanza la simulación, publica un `/cmd_vel` y verifica que llegan `/joint_states`

#### Documentación
- [ ] Añadir diagrama de topics y nodos (generado con `rqt_graph`) al README
- [ ] Documentar las diferencias de comportamiento entre Gazebo y MVSim para este modelo
- [ ] Añadir instrucciones para crear un mundo personalizado

---

## Estructura del paquete (objetivo)

```
caddy_ai2_ros2_sim/
├── config/
│   ├── controllers_sim.yaml    # Controladores para simulación
│   └── rviz/
│       └── sim.rviz            # Configuración de RViz
├── launch/
│   ├── sim.launch.py           # Wrapper — selecciona simulador por argumento
│   ├── sim_gazebo.launch.py    # Launch completo con Gazebo Harmonic
│   └── sim_mvsim.launch.py    # Launch completo con MVSim
├── worlds/
│   ├── empty.world             # Mundo vacío
│   └── field.world             # Campo agrícola básico
├── CMakeLists.txt
├── package.xml
└── README.md
```

---

## Licencia

Copyright (c) 2026, Rafael Carbonell Lázaro (racarla96) — CC BY 4.0
