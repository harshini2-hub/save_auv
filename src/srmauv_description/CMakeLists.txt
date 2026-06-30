cmake_minimum_required(VERSION 3.8)
project(srmauv_description)

find_package(ament_cmake REQUIRED)

# Install resource folders so launch files can locate them at runtime.
install(
  DIRECTORY urdf meshes launch worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
