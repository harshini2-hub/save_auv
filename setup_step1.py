#!/usr/bin/env python3
"""
Sets up the complete Step 1 underwater dynamics for the NIOT SAVe AUV:
  1. Creates the srmauv_dynamics package (drag plugin)
  2. Updates srmauv.urdf.xacro with buoyancy + drag plugin gazebo tags
  3. Prints exact commands to build and verify
"""
import os, shutil

SAVE_AUV = os.path.expanduser("~/save_auv")
SRC      = os.path.join(SAVE_AUV, "src")
PKG_DIR  = os.path.join(SRC, "srmauv_dynamics")
SRC_DIR  = os.path.join(PKG_DIR, "src")
URDF     = os.path.join(SAVE_AUV, "src/srmauv_description/urdf/srmauv.urdf.xacro")

# 1. Create package directory structure
os.makedirs(SRC_DIR, exist_ok=True)
print(f"Created {PKG_DIR}")

# 2. Write CMakeLists.txt
cmake = """cmake_minimum_required(VERSION 3.8)
project(srmauv_dynamics)

find_package(ament_cmake REQUIRED)
find_package(gazebo REQUIRED)

include_directories(${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

add_library(hydrodynamic_plugin SHARED src/drag_plugin.cpp)
target_link_libraries(hydrodynamic_plugin ${GAZEBO_LIBRARIES})

install(TARGETS hydrodynamic_plugin
  LIBRARY DESTINATION lib)

ament_package()
"""
with open(os.path.join(PKG_DIR, "CMakeLists.txt"), "w") as f:
    f.write(cmake)
print("Written CMakeLists.txt")

# 3. Write package.xml
pkg_xml = """<?xml version="1.0"?>
<package format="3">
  <name>srmauv_dynamics</name>
  <version>0.1.0</version>
  <description>Hydrodynamic drag and added mass plugin for NIOT SAVe AUV</description>
  <maintainer email="team@srmauv.local">SRM AUV Team</maintainer>
  <license>MIT</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <depend>gazebo_ros</depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
"""
with open(os.path.join(PKG_DIR, "package.xml"), "w") as f:
    f.write(pkg_xml)
print("Written package.xml")

# 4. Write drag_plugin.cpp
drag_cpp = r"""#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Vector3.hh>

namespace gazebo {

class HydrodynamicPlugin : public ModelPlugin {
 public:
  void Load(physics::ModelPtr model, sdf::ElementPtr sdf) override {
    model_ = model;
    link_  = model->GetLink("base_link");
    if (!link_) { gzerr << "[HydrodynamicPlugin] base_link not found!\n"; return; }

    if (sdf->HasElement("cd_linear"))    cd_lin_  = sdf->Get<double>("cd_linear");
    if (sdf->HasElement("cd_quadratic")) cd_quad_ = sdf->Get<double>("cd_quadratic");
    if (sdf->HasElement("cd_angular"))   cd_ang_  = sdf->Get<double>("cd_angular");
    if (sdf->HasElement("fluid_level"))  fluid_level_ = sdf->Get<double>("fluid_level");

    update_conn_ = event::Events::ConnectWorldUpdateBegin(
        std::bind(&HydrodynamicPlugin::OnUpdate, this));

    gzmsg << "[HydrodynamicPlugin] Loaded. cd_lin=" << cd_lin_
          << " cd_quad=" << cd_quad_ << " cd_ang=" << cd_ang_ << "\n";
  }

  void OnUpdate() {
    auto pose = link_->WorldPose();
    if (pose.Pos().Z() > fluid_level_) return;

    auto vel   = link_->WorldLinearVel();
    double spd = vel.Length();
    ignition::math::Vector3d drag = -(cd_lin_ + cd_quad_ * spd) * vel;
    ignition::math::Vector3d tdrag = -cd_ang_ * link_->WorldAngularVel();

    link_->AddForce(drag);
    link_->AddTorque(tdrag);
  }

 private:
  physics::ModelPtr    model_;
  physics::LinkPtr     link_;
  event::ConnectionPtr update_conn_;
  double cd_lin_      = 10.0;
  double cd_quad_     = 50.0;
  double cd_ang_      = 5.0;
  double fluid_level_ = 2.5;
};

GZ_REGISTER_MODEL_PLUGIN(HydrodynamicPlugin)
}  // namespace gazebo
"""
with open(os.path.join(SRC_DIR, "drag_plugin.cpp"), "w") as f:
    f.write(drag_cpp)
print("Written drag_plugin.cpp")

# 5. Update URDF — replace whatever buoyancy block exists (or closing robot tag)
#    with clean buoyancy + drag plugin block
with open(URDF) as f:
    content = f.read()

# Remove any existing gazebo plugin blocks we added before
import re
content = re.sub(r'\s*<gazebo>\s*<plugin name="buoyancy_plugin".*?</plugin>\s*</gazebo>', 
                 '', content, flags=re.DOTALL)

# Also remove if it somehow got duplicated
content = re.sub(r'\s*<gazebo>\s*<plugin name="hydrodynamic_plugin".*?</plugin>\s*</gazebo>', 
                 '', content, flags=re.DOTALL)

plugin_block = """
  <!-- ================================================================
       STEP 1: Underwater Dynamics
       Buoyancy: volume=0.020 m^3 = mass(20kg)/water_density(1000)
                 -> exact neutral buoyancy as the baseline.
                 With drag now present, this won't fly away.
       Drag: cd_linear=10, cd_quadratic=50 N/(m/s)^2, cd_angular=5
             These are realistic starting values for a 0.6m AUV.
       ================================================================ -->
  <gazebo>
    <plugin name="buoyancy_plugin" filename="libBuoyancyPlugin.so">
      <fluid_density>1000</fluid_density>
      <link name="base_link">
        <center_of_volume>0.0 -0.156 -0.117</center_of_volume>
        <volume>0.020</volume>
      </link>
    </plugin>
  </gazebo>

  <gazebo>
    <plugin name="hydrodynamic_plugin" filename="libhydrodynamic_plugin.so">
      <cd_linear>10.0</cd_linear>
      <cd_quadratic>50.0</cd_quadratic>
      <cd_angular>5.0</cd_angular>
      <fluid_level>2.5</fluid_level>
    </plugin>
  </gazebo>

</robot>
"""

# Remove closing robot tag and append our block
content = content.rstrip()
if content.endswith("</robot>"):
    content = content[:-len("</robot>")].rstrip()
content = content + "\n" + plugin_block

with open(URDF, "w") as f:
    f.write(content)
print("Updated srmauv.urdf.xacro with buoyancy + drag plugins")

# 6. Verify
print("\n=== Verification ===")
with open(URDF) as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if "buoyancy" in line or "hydrodynamic" in line or "volume" in line:
        print(f"  Line {i}: {line.rstrip()}")

print(f"""
=== Next steps ===
Run these commands:

  cd ~/save_auv
  colcon build
  source install/setup.bash

  # Tell Gazebo where to find the new plugin:
  export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:~/save_auv/install/srmauv_dynamics/lib

  pkill -9 -x gzserver; pkill -9 -x gzclient
  ros2 launch srmauv_description niot_mission.launch.py

After launch:
  - Click srmauv in entity tree, expand pose, note Z at spawn (~1.2)
  - Wait 15 seconds, note Z again
  - Expected: Z stays within ~0.5 of spawn height (not 3000, not 0.33)
  - Terminal: look for "[HydrodynamicPlugin] Loaded" from gzserver
""")
