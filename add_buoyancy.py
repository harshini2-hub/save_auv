#!/usr/bin/env python3
"""
Safely inserts the Gazebo buoyancy plugin into niot_mission.world,
right before the closing </world> tag. Run from anywhere.
"""
import os

WORLD = os.path.expanduser("~/save_auv/src/srmauv_description/worlds/niot_mission.world")

plugin_block = """    <plugin name="buoyancy_plugin" filename="libBuoyancyPlugin.so">
      <fluid_density>1000</fluid_density>
      <fluid_level>2.5</fluid_level>
      <link name="srmauv::base_link">
        <center_of_volume>0 0 0</center_of_volume>
        <volume>0.035</volume>
      </link>
    </plugin>
"""

with open(WORLD) as f:
    content = f.read()

if "buoyancy_plugin" in content:
    print("Buoyancy plugin already present — no changes made.")
else:
    idx = content.rfind("</world>")
    if idx == -1:
        print("ERROR: could not find </world> tag. Paste me the full file instead:")
        print(f"cat {WORLD}")
    else:
        new_content = content[:idx] + plugin_block + content[idx:]
        with open(WORLD, "w") as f:
            f.write(new_content)
        print("Buoyancy plugin inserted successfully.")
        print("Now run: cd ~/save_auv && colcon build && source install/setup.bash")
        print("Then:    ros2 launch srmauv_description niot_mission.launch.py")
