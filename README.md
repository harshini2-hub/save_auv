# SAVE AUV — NIOT Student AUV Simulation

Gazebo Classic 11 + ROS 2 Humble simulation of the SRM University AUV for the NIOT SAVe competition.

## Current Status
- ✅ Step 1: Buoyancy + hydrodynamic drag
- ✅ Step 2: 8 thrusters + keyboard teleop
- ✅ Step 3: IMU, depth sensor, front camera, bottom camera
- 🔲 Step 4: Autonomy

## Quick Start
```bash
cd ~/save_auv
colcon build
source install/setup.bash
export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:~/save_auv/install/srmauv_dynamics/lib
ros2 launch srmauv_description niot_mission.launch.py
```

## Teleop
```bash
python3 ~/save_auv/auv_teleop.py
```
W/S=forward/back | A/D=yaw | Q/E=strafe | R/F=up/down | SPACE=stop

## Topics
- /srmauv/imu
- /srmauv/depth
- /srmauv/front_camera/image_raw
- /srmauv/bottom_camera/image_raw
- /srmauv/thruster_1 to /srmauv/thruster_8
