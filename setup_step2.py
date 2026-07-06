#!/usr/bin/env python3
"""
Step 2: Adds 6 thrusters to srmauv.urdf.xacro
- 4 horizontal at 45 degrees (surge/sway/yaw)
- 2 vertical (heave)
Each thruster subscribes to /srmauv/thruster_N (std_msgs/Float64)
Force range: -40.2N to +51.5N (matching real T200 specs)
"""
import os, re

URDF = os.path.expanduser(
    "~/save_auv/src/srmauv_description/urdf/srmauv.urdf.xacro")

with open(URDF) as f:
    content = f.read()

# Remove any old thruster blocks we may have added before
content = re.sub(
    r'\s*<!-- STEP 2.*?<!-- END STEP 2 -->',
    '', content, flags=re.DOTALL)

thruster_block = """
  <!-- ================================================================
       STEP 2: Thrusters
       6x thruster layout based on real SRM AUV photos:
         T1 front-left  : +X+Y, 45deg yaw  (surge+sway+yaw)
         T2 front-right : +X-Y, -45deg yaw (surge+sway+yaw)
         T3 rear-left   : -X+Y, -45deg yaw (surge+sway+yaw)
         T4 rear-right  : -X-Y, 45deg yaw  (surge+sway+yaw)
         T5 vert-left   : +Y, pointing down (heave)
         T6 vert-right  : -Y, pointing down (heave)
       Topics: /srmauv/thruster_1 ... /srmauv/thruster_6 (std_msgs/Float64)
       Force range: -40.2N (reverse) to +51.5N (forward)
       ================================================================ -->

  <!-- Thruster joints (fixed, just for visual placement) -->
  <joint name="thruster_1_joint" type="fixed">
    <parent link="base_link"/>
    <child link="thruster_1_link"/>
    <origin xyz="0.20 0.18 0.0" rpy="0 0 0.785"/>
  </joint>
  <link name="thruster_1_link"/>

  <joint name="thruster_2_joint" type="fixed">
    <parent link="base_link"/>
    <child link="thruster_2_link"/>
    <origin xyz="0.20 -0.18 0.0" rpy="0 0 -0.785"/>
  </joint>
  <link name="thruster_2_link"/>

  <joint name="thruster_3_joint" type="fixed">
    <parent link="base_link"/>
    <child link="thruster_3_link"/>
    <origin xyz="-0.20 0.18 0.0" rpy="0 0 -0.785"/>
  </joint>
  <link name="thruster_3_link"/>

  <joint name="thruster_4_joint" type="fixed">
    <parent link="base_link"/>
    <child link="thruster_4_link"/>
    <origin xyz="-0.20 -0.18 0.0" rpy="0 0 0.785"/>
  </joint>
  <link name="thruster_4_link"/>

  <joint name="thruster_5_joint" type="fixed">
    <parent link="base_link"/>
    <child link="thruster_5_link"/>
    <origin xyz="0.0 0.18 -0.15" rpy="0 1.5708 0"/>
  </joint>
  <link name="thruster_5_link"/>

  <joint name="thruster_6_joint" type="fixed">
    <parent link="base_link"/>
    <child link="thruster_6_link"/>
    <origin xyz="0.0 -0.18 -0.15" rpy="0 1.5708 0"/>
  </joint>
  <link name="thruster_6_link"/>

  <!-- Thruster 1: front-left, 45deg, horizontal -->
  <gazebo>
    <plugin name="thruster_1" filename="libgazebo_ros_force.so">
      <ros>
        <namespace>/srmauv</namespace>
        <remapping>gazebo_ros_force:=thruster_1</remapping>
      </ros>
      <link_name>thruster_1_link</link_name>
      <force_frame>link</force_frame>
    </plugin>
  </gazebo>

  <!-- Thruster 2: front-right, -45deg, horizontal -->
  <gazebo>
    <plugin name="thruster_2" filename="libgazebo_ros_force.so">
      <ros>
        <namespace>/srmauv</namespace>
        <remapping>gazebo_ros_force:=thruster_2</remapping>
      </ros>
      <link_name>thruster_2_link</link_name>
      <force_frame>link</force_frame>
    </plugin>
  </gazebo>

  <!-- Thruster 3: rear-left, -45deg, horizontal -->
  <gazebo>
    <plugin name="thruster_3" filename="libgazebo_ros_force.so">
      <ros>
        <namespace>/srmauv</namespace>
        <remapping>gazebo_ros_force:=thruster_3</remapping>
      </ros>
      <link_name>thruster_3_link</link_name>
      <force_frame>link</force_frame>
    </plugin>
  </gazebo>

  <!-- Thruster 4: rear-right, 45deg, horizontal -->
  <gazebo>
    <plugin name="thruster_4" filename="libgazebo_ros_force.so">
      <ros>
        <namespace>/srmauv</namespace>
        <remapping>gazebo_ros_force:=thruster_4</remapping>
      </ros>
      <link_name>thruster_4_link</link_name>
      <force_frame>link</force_frame>
    </plugin>
  </gazebo>

  <!-- Thruster 5: vertical left, pointing down -->
  <gazebo>
    <plugin name="thruster_5" filename="libgazebo_ros_force.so">
      <ros>
        <namespace>/srmauv</namespace>
        <remapping>gazebo_ros_force:=thruster_5</remapping>
      </ros>
      <link_name>thruster_5_link</link_name>
      <force_frame>link</force_frame>
    </plugin>
  </gazebo>

  <!-- Thruster 6: vertical right, pointing down -->
  <gazebo>
    <plugin name="thruster_6" filename="libgazebo_ros_force.so">
      <ros>
        <namespace>/srmauv</namespace>
        <remapping>gazebo_ros_force:=thruster_6</remapping>
      </ros>
      <link_name>thruster_6_link</link_name>
      <force_frame>link</force_frame>
    </plugin>
  </gazebo>
  <!-- END STEP 2 -->
"""

# Insert before closing </robot>
content = content.rstrip()
if content.endswith("</robot>"):
    content = content[:-len("</robot>")].rstrip()
content = content + "\n" + thruster_block + "\n</robot>\n"

with open(URDF, "w") as f:
    f.write(content)

print("Thruster blocks written to URDF.")
print("\nVerifying...")
with open(URDF) as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if "thruster" in line.lower() and ("joint" in line.lower() or
                                        "plugin" in line.lower()):
        print(f"  Line {i}: {line.rstrip()}")

print("""
=== Next: build and test ===

  cd ~/save_auv
  colcon build
  source install/setup.bash
  export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:~/save_auv/install/srmauv_dynamics/lib
  pkill -9 -x gzserver; pkill -9 -x gzclient
  ros2 launch srmauv_description niot_mission.launch.py

Then in a second terminal, test forward thrust:
  source ~/save_auv/install/setup.bash
  ros2 topic pub /srmauv/thruster_1 geometry_msgs/msg/Wrench \
    "{force: {x: 25.0, y: 0.0, z: 0.0}, torque: {x: 0.0, y: 0.0, z: 0.0}}" \
    --once

Expected: vehicle moves forward-left (thruster 1 is front-left at 45deg)
""")
