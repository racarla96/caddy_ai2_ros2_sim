#!/usr/bin/env python3
"""Chase camera for demo videos: teleports the static model `spectator_cam` behind/left of the Caddy,
looking at it. Uses gz-transport directly (no gz CLI spawning). Stop with ~/record.stop."""
import math, os, time
from gz.transport13 import Node
from gz.msgs10.pose_v_pb2 import Pose_V
from gz.msgs10.pose_pb2 import Pose
from gz.msgs10.boolean_pb2 import Boolean

WORLD = "parking_garage_world"
BACK, SIDE, UP, LOOK_Z = 5.0, 2.6, 1.85, 0.8    # camera offset in the robot frame (m)
ALPHA = 0.18                                     # low-pass on the camera pose
robot = {}
def on_poses(msg):
    for p in msg.pose:
        if p.name == "caddy_ai2":
            q = p.orientation
            yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
            robot.update(x=p.position.x, y=p.position.y, z=p.position.z, yaw=yaw)
node = Node()
node.subscribe(Pose_V, f"/world/{WORLD}/dynamic_pose/info", on_poses)
cam = None
stop = os.path.expanduser("~/record.stop")
while not os.path.exists(stop):
    time.sleep(0.07)
    if not robot: continue
    x, y, z, yaw = robot["x"], robot["y"], robot["z"], robot["yaw"]
    cx = x - BACK * math.cos(yaw) - SIDE * math.sin(yaw)
    cy = y - BACK * math.sin(yaw) + SIDE * math.cos(yaw)
    cz = UP
    if cam is None: cam = [cx, cy, cz]
    else: cam = [cam[0] + ALPHA * (cx - cam[0]), cam[1] + ALPHA * (cy - cam[1]), cz]
    dx, dy = x - cam[0], y - cam[1]
    cyaw = math.atan2(dy, dx)
    pitch = math.atan2(cam[2] - LOOK_Z, math.hypot(dx, dy))   # positive = look down
    cy2, sy2, cp, sp = math.cos(cyaw / 2), math.sin(cyaw / 2), math.cos(pitch / 2), math.sin(pitch / 2)
    req = Pose(); req.name = "spectator_cam"
    req.position.x, req.position.y, req.position.z = cam
    req.orientation.w, req.orientation.x, req.orientation.y, req.orientation.z = cy2 * cp, 0.0, cy2 * sp, sy2 * cp
    node.request(f"/world/{WORLD}/set_pose", req, Pose, Boolean, 300)
