# tools — vídeos de demostración desde Gazebo

Cámara espectadora que sigue al Caddy y grabador a MP4. Sirven con el servidor de Gazebo **sin
pantalla** (`headless:=true`): la cámara se renderiza en la GPU del servidor, no hace falta GUI.

```bash
SHARE=$(ros2 pkg prefix caddy_ai2_ros2_sim)/share/caddy_ai2_ros2_sim/tools
export PYTHONPATH=/opt/ros/jazzy/opt/gz_transport_vendor/lib/python:/opt/ros/jazzy/opt/gz_msgs_vendor/lib/python:$PYTHONPATH

# 1) insertar la cámara en el mundo en marcha y puentearla a ROS
gz service -s /world/parking_garage_world/create --reqtype gz.msgs.EntityFactory \
  --reptype gz.msgs.Boolean --timeout 5000 --req "sdf_filename: \"$SHARE/spectator_cam.sdf\""
ros2 run ros_gz_bridge parameter_bridge "/spectator/image@sensor_msgs/msg/Image[gz.msgs.Image" &

# 2) que la cámara siga al robot (se detiene creando ~/record.stop)
python3 $SHARE/follow_cam.py &

# 3) grabar 40 s (o hasta ~/record.stop)
python3 $SHARE/record_gz.py ~/demo.mp4 40
```

`record_gz.py <salida> <segundos> [snap]` guarda MP4 (mp4v); con `snap` guarda un PNG y sale.
Recodifica para compartir: `ffmpeg -i demo.mp4 -c:v libx264 -crf 20 -pix_fmt yuv420p demo_h264.mp4`.

- El nombre del mundo en `follow_cam.py` (`WORLD`) y en el comando de `gz service` es el de
  `<world name=...>` del SDF (en el parking: `parking_garage_world`).
- La cámara espectadora va por encima del robot a ~1,85 m: el techo del parking es bajo.
