# 🚜 Autonomous Agricultural Rover

An AI-enabled autonomous agricultural rover designed to assist in **smart farming, crop monitoring, environmental sensing, and autonomous navigation**. The system combines **ROS 2, Gazebo simulation, Nav2, LiDAR-based obstacle detection, sensor data, GPS/location information, and YOLO-based plant detection** to create a software-driven agricultural monitoring platform.

---

## 📌 Project Overview

Traditional agricultural monitoring requires significant manual effort to inspect crops and collect field data. This project proposes an **Autonomous Agricultural Rover** capable of navigating agricultural environments, collecting environmental information, identifying plants, and presenting the collected data through a monitoring dashboard.

The rover is developed primarily as a **software and simulation-based system**, allowing autonomous navigation and AI-based agricultural analysis without requiring physical hardware during the development stage.

---

## 🎯 Objectives

The main objectives of the project are:

1. 🌱 Measure **soil moisture, temperature, and humidity**.
2. 📍 Associate plant detections and sensor measurements with **rover location and timestamp**.
3. 📊 Develop a dashboard displaying:

   * Navigation status
   * Sensor readings
   * AI detection results
   * Rover status
4. 🤖 Integrate a **YOLO-based computer vision model** to detect healthy and potentially diseased plants.
5. 🧭 Evaluate:

   * Navigation accuracy
   * Obstacle avoidance
   * Plant detection performance
   * Sensor-data collection
   * Overall system performance

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │   Agricultural Field    │
                    │       Simulation        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     ROS 2 Environment   │
                    │       (Jazzy)           │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
      ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
      │   Sensors   │    │   LiDAR      │    │   Camera     │
      │             │    │              │    │              │
      │ Soil        │    │ /scan        │    │ Image Input  │
      │ Moisture    │    │ /scan/points │    │              │
      │ Temperature │    │              │    │              │
      │ Humidity    │    │              │    │              │
      └──────┬──────┘    └──────┬───────┘    └──────┬───────┘
             │                  │                   │
             ▼                  ▼                   ▼
      ┌──────────────────────────────────────────────────┐
      │                  ROS 2 Processing                │
      │                                                  │
      │  Sensor Processing │ SLAM │ Localization │ Nav2  │
      └───────────────────────────┬──────────────────────┘
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
             ┌──────────────┐         ┌────────────────┐
             │ Autonomous   │         │ YOLO Detection │
             │ Navigation   │         │                │
             └──────┬───────┘         └───────┬────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │     Data Dashboard      │
                    │                         │
                    │ Navigation │ Sensors    │
                    │ AI Results │ Rover State│
                    └─────────────────────────┘
```

---

## 🛠️ Technologies Used

### Robotics & Simulation

* **ROS 2 Jazzy**
* **Gazebo Sim**
* **Nav2**
* **RViz2**
* **SLAM / Localization**
* **TF / TF2**
* **ROS 2 Topics & Services**

### Programming

* **Python**
* **C++**
* **Bash**

### AI / Computer Vision

* **YOLO**
* **OpenCV**
* Computer Vision
* Image Classification / Object Detection

### Sensors & Data

* LiDAR
* Camera
* Soil Moisture Sensor
* Temperature Sensor
* Humidity Sensor
* GPS / Location Data

### Development Environment

* Ubuntu 24.04 LTS
* Windows 11
* WSL 2
* Git & GitHub

---

## 📂 Project Structure

```text
autonomous-agricultural-rover/
│
├── src/
│   ├── rover_description/
│   │   ├── urdf/
│   │   ├── meshes/
│   │   └── launch/
│   │
│   ├── rover_gazebo/
│   │   ├── worlds/
│   │   ├── models/
│   │   └── launch/
│   │
│   ├── rover_navigation/
│   │   ├── config/
│   │   ├── maps/
│   │   └── launch/
│   │
│   ├── sensor_processing/
│   │   ├── scripts/
│   │   └── config/
│   │
│   ├── plant_detection/
│   │   ├── models/
│   │   ├── datasets/
│   │   └── scripts/
│   │
│   └── rover_dashboard/
│       ├── frontend/
│       └── backend/
│
├── config/
│
├── launch/
│
├── maps/
│
├── models/
│
├── screenshots/
│
├── docs/
│
├── requirements.txt
├── README.md
└── LICENSE
```

> Folder names can be adjusted to match the actual ROS 2 packages in your repository.

---

# 🚀 Features

### 🧭 Autonomous Navigation

The rover uses **ROS 2 Nav2** for autonomous navigation and path planning.

Key capabilities include:

* Map-based navigation
* Goal-based movement
* Path planning
* Obstacle avoidance
* Localization
* Velocity control
* Navigation status monitoring

---

### 📡 LiDAR-Based Obstacle Detection

LiDAR provides information about the surrounding environment.

Important ROS 2 topics include:

```text
/scan
/scan/points
```

The LiDAR data can be used by the navigation stack for:

* Obstacle detection
* Local costmap generation
* Collision avoidance
* Navigation planning

---

### 🌱 Agricultural Sensor Monitoring

The system is designed to collect:

```text
Soil Moisture
Temperature
Humidity
```

Each measurement can be associated with:

```text
Sensor Value
Timestamp
Rover Position
```

This allows the system to build a location-based record of field conditions.

---

### 🤖 AI-Based Plant Detection

A YOLO-based object detection model is integrated/planned for identifying plants from camera images.

Example detection categories:

```text
Healthy Plant
Potentially Diseased Plant
```

The detected information can be combined with rover position and timestamp.

---

### 📊 Monitoring Dashboard

The dashboard provides a centralized view of rover operation.

Example information:

```text
┌────────────────────────────────────┐
│      AUTONOMOUS AGRICULTURAL ROVER │
├────────────────────────────────────┤
│ Navigation Status: ACTIVE          │
│ Rover Position: (X, Y)             │
│ Battery Status: ---                │
├────────────────────────────────────┤
│ Soil Moisture: ---                 │
│ Temperature: --- °C                │
│ Humidity: --- %                    │
├────────────────────────────────────┤
│ Plant Detection                    │
│ Healthy: ---                       │
│ Potential Disease: ---             │
└────────────────────────────────────┘
```

---

# 📊 Performance Evaluation

The project can be evaluated using the following metrics:

| Parameter          | Evaluation Metric         |
| ------------------ | ------------------------- |
| Navigation         | Position error            |
| Path Planning      | Path length               |
| Obstacle Avoidance | Successful avoidance rate |
| Plant Detection    | Precision, Recall, mAP    |
| Sensor Monitoring  | Measurement accuracy      |
| Localization       | Position error            |
| System Performance | Processing time / FPS     |

---

# 🔮 Future Scope

Future improvements may include:

* Real-time field mapping
* Improved plant disease classification
* Multi-rover coordination
* Advanced crop health analysis
* Weed detection
* Yield estimation
* Weather-data integration
* Cloud-based agricultural analytics
* Real-time GPS tracking
* Autonomous field coverage planning
* Historical crop-health analysis

---

# 👨‍💻 Skills Demonstrated

* ROS 2
* Gazebo Simulation
* Nav2
* Autonomous Navigation
* SLAM & Localization
* LiDAR Processing
* Sensor Integration
* Python
* C++
* C
