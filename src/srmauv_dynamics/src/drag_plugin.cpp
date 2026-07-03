#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Vector3.hh>

namespace gazebo {

class HydrodynamicPlugin : public ModelPlugin {
 public:
  void Load(physics::ModelPtr model, sdf::ElementPtr sdf) override {
    model_ = model;

    // When spawned via spawn_entity (URDF), Gazebo prefixes link names
    // with the model name: "base_footprint" becomes "srmauv::base_link".
    // Try both forms so this works whether loaded from SDF or URDF.
    link_ = model->GetLink("base_footprint");
    if (!link_) link_ = model->GetLink(model->GetName() + "::base_link");
    if (!link_) {
      // Last resort: just grab the first link in the model
      auto links = model->GetLinks();
      for (auto& l : links) {
        if (l->GetName().find("base_footprint") != std::string::npos) {
          link_ = l;
          break;
        }
      }
    }
    if (!link_) {
      gzerr << "[HydrodynamicPlugin] Could not find base_link in model '"
            << model->GetName() << "'. Available links:\n";
      for (auto& l : model->GetLinks())
        gzerr << "  " << l->GetName() << "\n";
      return;
    }

    if (sdf->HasElement("cd_linear"))    cd_lin_      = sdf->Get<double>("cd_linear");
    if (sdf->HasElement("cd_quadratic")) cd_quad_     = sdf->Get<double>("cd_quadratic");
    if (sdf->HasElement("cd_angular"))   cd_ang_      = sdf->Get<double>("cd_angular");
    if (sdf->HasElement("fluid_level"))  fluid_level_ = sdf->Get<double>("fluid_level");

    update_conn_ = event::Events::ConnectWorldUpdateBegin(
        std::bind(&HydrodynamicPlugin::OnUpdate, this));

    gzmsg << "[HydrodynamicPlugin] Loaded on link '" << link_->GetName()
          << "'. cd_lin=" << cd_lin_
          << " cd_quad=" << cd_quad_
          << " cd_ang=" << cd_ang_
          << " fluid_level=" << fluid_level_ << "\n";
  }

  void OnUpdate() {
    if (!link_) return;

    // Only apply drag when the link centre is below the fluid surface
    auto pose = link_->WorldPose();
    if (pose.Pos().Z() > fluid_level_) return;

    auto vel   = link_->WorldLinearVel();
    double spd = vel.Length();

    // Quadratic drag: F = -(Cd_lin + Cd_quad * |v|) * v
    ignition::math::Vector3d drag  = -(cd_lin_ + cd_quad_ * spd) * vel;
    // Angular drag:   τ = -Cd_ang * ω
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
