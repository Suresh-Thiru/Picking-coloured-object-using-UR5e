# Picking-coloured-object-using-UR5e
Picking the coloured object on the work table using robotiq camera and OpenCV

“See It, Pick It!” 🔍🤖

Another Weekend Wrap: just for fun (and a bit of a challenge) I dove into vision-based robotic picking using our UR5e and the Robotiq wrist camera.

Over the weekend, I put together a quick demo that:

📸 Captures an image from the Robotiq wrist camera via URCap

🎨 Uses OpenCV in Python to detect object color

🗣️ Leverages Google Speech API to issue voice commands (“Pick the red one”, “Pick the blue one”, etc.)

🤖 Sends pick/place commands back to the UR5e

Main challenge:
Getting a live video feed through the URCap interface proved trickier than expected. I worked around it by grabbing single-frame snapshots, then converting the detected pixel location into real-world coordinates for the robot to act on.

Tech stack:

Python + OpenCV (no GUI)

Google Speech API for voice control

Robotiq Wrist Camera with URCap

Universal Robots UR5e

What’s next?

Stream live video via a custom URCap plugin

Refine pixel-to-coordinate mapping with camera calibration

Integrate an AI-based vision model (e.g., TensorFlow or PyTorch) for more robust object detection

Add a ROS bridge for multi-modal control (gesture + voice + vision)

🔗 Check out the project video here for a quick demo!

#UR5e #Robotics #ComputerVision #OpenCV #VoiceControl #Python #Automation #WeekendBuild #IndustrialRobotics #HumanRobotInteraction #Robotiq #UniversalRobots #JustForFun
