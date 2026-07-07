# SAVE AUV — NIOT Student AUV Simulation

Gazebo Classic 11 + ROS 2 Humble simulation of the SRM University AUV for the NIOT SAVe competition.

## Current Status
- ✅ Step 1: Underwater dynamics — buoyancy + hydrodynamic drag (vehicle hovers at neutral buoyancy)
- ✅ Step 2: 8 thrusters + keyboard teleop
- 🔲 Step 3: Sensors (IMU, depth, cameras)
- 🔲 Step 4: Autonomy

## Quick Start
```bash
cd ~/save_auv
colcon build
source install/setup.bash
export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:~/save_auv/install/srmauv_dynamics/lib
ros2 launch srmauv_description niot_mission.launch.py
```

## Teleop Control
```bash
source ~/save_auv/install/setup.bash
python3 ~/save_auv/auv_teleop.py
```
W/S = forward/back | A/D = yaw | Q/E = strafe | R/F = up/down | SPACE = stop
