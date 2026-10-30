#!/usr/bin/env python3
import rclpy, sys, os, time, cv2, numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
out, dur, mode = sys.argv[1], float(sys.argv[2]), (sys.argv[3] if len(sys.argv) > 3 else "rec")
rclpy.init(); n = Node("gz_recorder"); st = {"w": None, "n": 0, "t0": None}
def cb(m):
    a = np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.width, -1)
    bgr = cv2.cvtColor(a, cv2.COLOR_RGB2BGR) if m.encoding == "rgb8" else a
    if mode == "snap":
        cv2.imwrite(out, bgr); st["n"] = 1; return
    if st["w"] is None:
        st["w"] = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (m.width, m.height)); st["t0"] = time.time()
    st["w"].write(bgr); st["n"] += 1
n.create_subscription(Image, "/spectator/image", cb, qos_profile_sensor_data)
t = time.time()
while rclpy.ok() and time.time() - t < dur and not os.path.exists(os.path.expanduser("~/record.stop")):
    rclpy.spin_once(n, timeout_sec=0.1)
    if mode == "snap" and st["n"]: break
if st["w"]: st["w"].release()
print("frames:", st["n"], "->", out)
