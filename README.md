
# Object Detection with ESP32-CAM & Arduino

## Overview
This project implements a real-time object detection system using the ESP32-CAM, Arduino UNO, and YOLOv3 for detecting living and non-living objects. It combines hardware components for movement and sensing with a Flask-based web interface for visualization.

## Features
- **Real-time Object Detection** using YOLOv3.
- **ESP32-CAM Video Streaming** with multiple resolutions.
- **Distance Measurement** using an ultrasonic sensor.
- **Autonomous Movement Control** for forward, backward, left, and right turns.
- **Web Interface** for live streaming and detection visualization.

## Hardware Components
- Arduino UNO  
- ESP32-CAM  
- L298N Motor Driver  
- HC-05 Bluetooth Module  
- DC Motors  
- Ultrasonic Sensor  
- LED  
- Buzzer  

## Software Components
- Arduino IDE  
- Visual Studio Code  
- Flask (Python)  
- OpenCV  
- YOLOv3  

## System Workflow
1. **Arduino UNO** controls the motors and movement based on commands.
2. **ESP32-CAM** captures images, measures distances, and streams video.
3. **Python Flask Server** loads YOLOv3, processes frames, and sends detection updates.
4. **Web Interface** displays the live video feed with detection labels and confidence levels.

## Pin Configuration
### Arduino UNO
- Pin 13: Left motors forward  
- Pin 12: Left motors reverse  
- Pin 11: Right motors forward  
- Pin 10: Right motors reverse  
- Pin 9: Motor Stop pin  

### ESP32-CAM
- TrigPin → OUTPUT (ultrasonic)  
- EchoPin → INPUT (ultrasonic)  
- Buzz pin → OUTPUT (buzzer)  
- MotorStopPin → OUTPUT  

## Web Server Endpoints
- `/cam-lo.jpg` – Low-resolution image  
- `/cam-mid.jpg` – Medium-resolution image  
- `/cam-hi.jpg` – High-resolution image  
- `/update_detection` – Receives detection results (living/non-living)  

## Execution Steps
1. Flash Arduino UNO with motor control logic.  
2. Configure ESP32-CAM with camera and Wi-Fi setup.  
3. Run the Flask server to start YOLO detection and serve the web interface.  
4. Access the live feed via browser and monitor detection results.  

## Detection Logic
- YOLOv3 detects objects from the ESP32-CAM feed.  
- Detected objects are classified with confidence scores.  
- The system stops or alerts based on proximity and object type.  

## Applications
- Smart trains and robotics.  
- Automated surveillance systems.  
- Obstacle detection and avoidance.  
