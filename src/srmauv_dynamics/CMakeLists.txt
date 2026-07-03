cmake_minimum_required(VERSION 3.8)
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
