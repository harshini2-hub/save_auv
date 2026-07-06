#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo_ros/node.hpp>
#include <std_msgs/msg/float64.hpp>
#include <ignition/math/Vector3.hh>
#include <memory>
#include <mutex>
#include <cmath>
#include <array>

namespace gazebo {

struct Thruster {
  ignition::math::Vector3d offset;
  ignition::math::Vector3d axis;
  double force = 0.0;
  double max_f = 51.5;
  double min_f = -40.2;
};

class AllThrustersPlugin : public ModelPlugin {
 public:
  void Load(physics::ModelPtr model, sdf::ElementPtr sdf) override {
    model_    = model;
    ros_node_ = gazebo_ros::Node::Get(sdf);

    link_ = model->GetLink("base_link");
    if (!link_) {
      for (auto& l : model->GetLinks())
        if (l->GetName().find("base_link") != std::string::npos)
          { link_ = l; break; }
    }
    if (!link_) { gzerr << "[AllThrustersPlugin] base_link not found!\n"; return; }

    // 8 thruster layout from real SRM AUV photos
    // 4 horizontal at 45deg corners + 4 vertical
    double s = 0.7071;
    thrusters_[0] = {{ 0.20,  0.18, 0.0}, { s,  s, 0}};  // T1 front-left  45deg
    thrusters_[1] = {{ 0.20, -0.18, 0.0}, { s, -s, 0}};  // T2 front-right -45deg
    thrusters_[2] = {{-0.20,  0.18, 0.0}, { s, -s, 0}};  // T3 rear-left   -45deg
    thrusters_[3] = {{-0.20, -0.18, 0.0}, { s,  s, 0}};  // T4 rear-right  45deg
    thrusters_[4] = {{ 0.20,  0.18,-0.15}, {0,  0, -1}};  // T5 front-vert-left
    thrusters_[5] = {{ 0.20, -0.18,-0.15}, {0,  0, -1}};  // T6 front-vert-right
    thrusters_[6] = {{-0.20,  0.18,-0.15}, {0,  0, -1}};  // T7 rear-vert-left
    thrusters_[7] = {{-0.20, -0.18,-0.15}, {0,  0, -1}};  // T8 rear-vert-right

    for (int i = 0; i < 8; i++) {
      std::string topic = "/srmauv/thruster_" + std::to_string(i + 1);
      int idx = i;
      auto sub = ros_node_->create_subscription<std_msgs::msg::Float64>(
          topic, 10,
          [this, idx](const std_msgs::msg::Float64::SharedPtr msg) {
            std::lock_guard<std::mutex> lock(mutex_);
            thrusters_[idx].force = std::max(
                thrusters_[idx].min_f,
                std::min(thrusters_[idx].max_f, msg->data));
          });
      subs_.push_back(sub);
      gzmsg << "[AllThrustersPlugin] Subscribed to " << topic << "\n";
    }

    update_conn_ = event::Events::ConnectWorldUpdateBegin(
        std::bind(&AllThrustersPlugin::OnUpdate, this));

    gzmsg << "[AllThrustersPlugin] Loaded on '" << link_->GetName()
          << "' — 8 thrusters ready\n";
  }

  void OnUpdate() {
    if (!link_) return;
    std::lock_guard<std::mutex> lock(mutex_);
    auto rot = link_->WorldPose().Rot();
    auto com = link_->WorldCoGPose().Pos();
    for (auto& t : thrusters_) {
      if (std::abs(t.force) < 1e-6) continue;
      auto world_axis   = rot.RotateVector(t.axis);
      auto world_offset = rot.RotateVector(t.offset);
      link_->AddForceAtWorldPosition(world_axis * t.force, com + world_offset);
    }
  }

 private:
  physics::ModelPtr   model_;
  physics::LinkPtr    link_;
  gazebo_ros::Node::SharedPtr ros_node_;
  std::vector<rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr> subs_;
  event::ConnectionPtr update_conn_;
  std::mutex mutex_;
  std::array<Thruster, 8> thrusters_;
};

GZ_REGISTER_MODEL_PLUGIN(AllThrustersPlugin)
}
