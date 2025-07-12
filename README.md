# Picking-coloured-object-using-UR5e
Picking the coloured object on the work table using robotiq camera and OpenCV

“See It, Pick It!” 🔍🤖

Another Weekend Wrap: just for learning. I dove into vision-based robotic pick and place using UR5e and the Robotiq wrist camera.

Over the weekend, I put together a quick demo that:

📸 Captures an image from the Robotiq wrist camera without UR Cap.
🎨 Uses OpenCV in Python to detect object color.
🗣️ Leverages Google Speech API to issue voice commands to pick a color (“Red,” “Yellow,” or “Green”).
🤖 Sends pick/place commands back to the UR5e.

Main challenge:
Working with the Robotiq wrist camera with UR Cap is a bit easy, as it guides the process of pick and place, but I had other ideas. 

I worked to connect with the camera and grab a single-frame snapshot, then convert the detected pixel location of the colored object using OpenCV into real-world coordinates for the robot to act on.

While these implementations demonstrate foundational-level control of the UR5e, they serve as a critical stepping stone toward advanced AI-driven machine vision and machine learning applications. Think real-time convolutional neural network⁠-based object recognition, sensor fusion, and reinforcement learning for adaptive grasping.

🛠️ Tech stack:
Python + OpenCV (no GUI)
Google Speech API for voice control
Robotiq Wrist Camera
Universal Robots UR5e

💡 What could be improved or taken further:

1. Integrate an AI-based vision model (e.g., TensorFlow or PyTorch) for more robust object detection.
2. Add a ROS bridge for multi-modal control (gesture + voice + vision).

Diving deep into OpenCV and voice-guided manipulation is all about preparing for tomorrow’s vehicle-centric smart manufacturing and skills to tackle vision challenges in self-driving cars.

Youtube link: https://youtu.be/X-wuH-tP2zE

hashtag#UR5e hashtag#Robotics hashtag#ComputerVision hashtag#OpenCV hashtag#VoiceControl hashtag#Python hashtag#Automation hashtag#WeekendBuild hashtag#IndustrialRobotics hashtag#HumanRobotInteraction hashtag#Robotiq hashtag#UniversalRobots hashtag#JustForFun hashtag#Robotiqwristcamera hashtag#Autonomousdriving hashtag#AstonUniversity hashtag#ADAS
