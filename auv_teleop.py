#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import sys, tty, termios

THRUST = 25.0

# Mixing matrix [T1,T2,T3,T4,T5,T6,T7,T8]
MOVES = {
    'w': [ 1,  1,  1,  1,  0,  0,  0,  0],  # forward
    's': [-1, -1, -1, -1,  0,  0,  0,  0],  # backward
    'a': [-1,  1, -1,  1,  0,  0,  0,  0],  # yaw left
    'd': [ 1, -1,  1, -1,  0,  0,  0,  0],  # yaw right
    'q': [-1,  1,  1, -1,  0,  0,  0,  0],  # strafe left
    'e': [ 1, -1, -1,  1,  0,  0,  0,  0],  # strafe right
    'r': [ 0,  0,  0,  0, -1, -1, -1, -1],  # up
    'f': [ 0,  0,  0,  0,  1,  1,  1,  1],  # down
}

LABELS = {
    'w':'Forward','s':'Backward','a':'Yaw Left','d':'Yaw Right',
    'q':'Strafe Left','e':'Strafe Right','r':'Up','f':'Down'
}

HELP = """
AUV Keyboard Control (8 Thrusters)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  W / S  →  Forward / Backward
  A / D  →  Yaw Left / Right
  Q / E  →  Strafe Left / Right
  R / F  →  Up / Down
  SPACE  →  Stop
  X      →  Quit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

class TeleopNode(Node):
    def __init__(self):
        super().__init__('auv_teleop')
        self.pubs = [
            self.create_publisher(Float64, f'/srmauv/thruster_{i}', 10)
            for i in range(1, 9)
        ]

    def send(self, mix):
        for i, m in enumerate(mix):
            msg = Float64()
            msg.data = float(m * THRUST)
            self.pubs[i].publish(msg)

    def stop(self):
        self.send([0]*8)

def main():
    rclpy.init()
    node = TeleopNode()
    settings = termios.tcgetattr(sys.stdin)
    print(HELP)
    try:
        while True:
            key = get_key(settings)
            if key == 'x':
                node.stop(); print("Quit."); break
            elif key == ' ':
                node.stop(); print("STOP")
            elif key.lower() in MOVES:
                node.send(MOVES[key.lower()])
                print(f"→ {LABELS[key.lower()]}  ({THRUST}N)")
            else:
                node.stop()
    except Exception as e:
        print(e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
