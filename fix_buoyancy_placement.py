#!/usr/bin/env python3
"""
Fixes the buoyancy plugin placement:
BuoyancyPlugin is a MODEL plugin, not a world plugin. It must go
INSIDE the <model name="srmauv"> ... </model> block, right before
that model's closing </model> tag -- not loose in the world.

This script:
 1. Removes the old (wrongly placed) world-level buoyancy plugin block
 2. Finds <model name='srmauv'> ... </model> and inserts the plugin
    correctly inside it, just before its closing </model> tag.
"""
import re
import os

WORLD = os.path.expanduser("~/save_auv/src/srmauv_description/worlds/niot_mission.world")

with open(WORLD) as f:
    content = f.read()

# 1. Remove old world-level plugin block (between <plugin name="buoyancy_plugin" and matching </plugin>)
old_pattern = re.compile(
    r'\s*<plugin name="buoyancy_plugin".*?</plugin>\s*', re.DOTALL
)
content, n_removed = old_pattern.subn("\n", content)
print(f"Removed {n_removed} old (incorrectly placed) buoyancy plugin block(s).")

# 2. Find the srmauv model block. Handles both 'srmauv' and "srmauv" quoting.
model_pattern = re.compile(
    r"(<model\s+name=['\"]srmauv['\"][^>]*>)(.*?)(</model>)", re.DOTALL
)

match = model_pattern.search(content)
if not match:
    print("ERROR: could not find <model name='srmauv'> in the world file.")
    print("This likely means the AUV is spawned separately via URDF/spawn_entity,")
    print("not present as a model block inside niot_mission.world itself.")
    print("\nIn that case the plugin needs to go in the URDF instead. Run:")
    print("  grep -n 'gazebo_ros\\|<gazebo' ~/save_auv/src/srmauv_description/urdf/srmauv.urdf.xacro")
    print("and paste me the output.")
else:
    plugin_block = '''
    <plugin name="buoyancy_plugin" filename="libBuoyancyPlugin.so">
      <fluid_density>1000</fluid_density>
      <link name="base_link">
        <center_of_volume>0 0 0</center_of_volume>
        <volume>0.035</volume>
      </link>
    </plugin>
  '''
    open_tag, body, close_tag = match.groups()
    new_model_block = open_tag + body + plugin_block + close_tag
    content = content[:match.start()] + new_model_block + content[match.end():]

    with open(WORLD, "w") as f:
        f.write(content)

    print("Buoyancy plugin correctly placed INSIDE the srmauv model.")
    print("Now run:")
    print("  cd ~/save_auv && colcon build && source install/setup.bash")
    print("  ros2 launch srmauv_description niot_mission.launch.py")
