cmake_minimum_required(VERSION 3.8)
project(srmauv_dynamics)

find_package(ament_cmake REQUIRED)
find_package(gazebo REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rclcpp REQUIRED)

include_directories(${GAZEBO_INCLUDE_DIRS} ${gazebo_ros_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

add_library(hydrodynamic_plugin SHARED src/drag_plugin.cpp)
target_link_libraries(hydrodynamic_plugin ${GAZEBO_LIBRARIES})

add_library(thruster_plugin SHARED src/thruster_plugin.cpp)
ament_target_dependencies(thruster_plugin gazebo_ros std_msgs rclcpp)
target_link_libraries(thruster_plugin ${GAZEBO_LIBRARIES} ${gazebo_ros_LIBRARIES})

install(TARGETS hydrodynamic_plugin thruster_plugin
  LIBRARY DESTINATION lib)

ament_package()
