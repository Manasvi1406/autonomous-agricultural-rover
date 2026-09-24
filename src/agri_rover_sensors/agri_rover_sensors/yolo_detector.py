#!/usr/bin/env python3

import os
import sys
import csv
import time

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.time import Time

from sensor_msgs.msg import Image
from std_msgs.msg import String, Float32

import tf2_ros


# =========================================================
# Add YOLO virtual environment packages
# =========================================================

YOLO_SITE_PACKAGES = os.path.expanduser(
    "~/agri_rover_ws/yolo/venv/lib/python3.12/site-packages"
)

if os.path.exists(YOLO_SITE_PACKAGES):
    sys.path.insert(0, YOLO_SITE_PACKAGES)

from ultralytics import YOLO


class YOLODetector(Node):

    def __init__(self):

        super().__init__("yolo_detector")

        # =================================================
        # YOLO MODEL
        # =================================================

        self.model_path = os.path.expanduser(
            "~/agri_rover_ws/yolo/runs/detect/train-4/weights/best.pt"
        )

        self.get_logger().info(
            f"Loading YOLO model: {self.model_path}"
        )

        self.model = YOLO(self.model_path)

        self.get_logger().info(
            "YOLO model loaded successfully."
        )

        # =================================================
        # CAMERA SUBSCRIBER
        # =================================================

        self.image_subscription = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            10
        )

        # =================================================
        # YOLO DETECTION PUBLISHER
        # =================================================

        self.detection_publisher = self.create_publisher(
            String,
            "/yolo/detections",
            10
        )

        # =================================================
        # SENSOR VALUES
        # =================================================

        self.soil_moisture = None
        self.temperature = None
        self.humidity = None

        self.soil_subscription = self.create_subscription(
            Float32,
            "/soil_moisture",
            self.soil_callback,
            10
        )

        self.temperature_subscription = self.create_subscription(
            Float32,
            "/temperature",
            self.temperature_callback,
            10
        )

        self.humidity_subscription = self.create_subscription(
            Float32,
            "/humidity",
            self.humidity_callback,
            10
        )

        # =================================================
        # TF2
        # =================================================

        self.tf_buffer = tf2_ros.Buffer()

        self.tf_listener = tf2_ros.TransformListener(
            self.tf_buffer,
            self
        )

        # =================================================
        # CSV FILE
        # =================================================

        self.csv_path = os.path.expanduser(
            "~/agri_rover_ws/yolo_detections.csv"
        )

        self.create_csv()

        # =================================================
        # COUNTERS
        # =================================================

        self.frame_count = 0
        self.detection_count = 0
        self.skipped_frames = 0

        # =================================================
        # STARTUP STATUS
        # =================================================

        self.get_logger().info(
            f"Detection CSV: {self.csv_path}"
        )

        self.get_logger().info(
            "YOLO agricultural detection system ready."
        )

    # =====================================================
    # CREATE CSV
    # =====================================================

    def create_csv(self):

        if not os.path.exists(self.csv_path):

            with open(
                self.csv_path,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "timestamp",
                    "frame",
                    "x",
                    "y",
                    "plant_class",
                    "confidence",
                    "x1",
                    "y1",
                    "x2",
                    "y2",
                    "soil_moisture",
                    "temperature",
                    "humidity"
                ])

    # =====================================================
    # SOIL MOISTURE CALLBACK
    # =====================================================

    def soil_callback(self, msg):

        self.soil_moisture = float(msg.data)

    # =====================================================
    # TEMPERATURE CALLBACK
    # =====================================================

    def temperature_callback(self, msg):

        self.temperature = float(msg.data)

    # =====================================================
    # HUMIDITY CALLBACK
    # =====================================================

    def humidity_callback(self, msg):

        self.humidity = float(msg.data)

    # =====================================================
    # GET ROVER POSITION
    # =====================================================

    def get_rover_position(self):

        try:

            # Time() requests the latest available transform
            transform = self.tf_buffer.lookup_transform(
                "map",
                "base_link",
                Time()
            )

            x = transform.transform.translation.x
            y = transform.transform.translation.y

            return float(x), float(y)

        except Exception as e:

            return None, None

    # =====================================================
    # CONVERT ROS IMAGE TO NUMPY
    # =====================================================

    def ros_image_to_numpy(self, msg):

        image = np.frombuffer(
            msg.data,
            dtype=np.uint8
        )

        image = image.reshape(
            (msg.height, msg.width, 3)
        )

        return image

    # =====================================================
    # CAMERA CALLBACK
    # =====================================================

    def image_callback(self, msg):

        self.frame_count += 1

        start_time = time.time()

        try:

            # ---------------------------------------------
            # Convert ROS image
            # ---------------------------------------------

            image = self.ros_image_to_numpy(msg)

            # ---------------------------------------------
            # Get rover position BEFORE recording results
            # ---------------------------------------------

            x, y = self.get_rover_position()

            # ---------------------------------------------
            # If TF is not ready, skip this frame
            # ---------------------------------------------

            if x is None or y is None:

                self.skipped_frames += 1

                if self.skipped_frames <= 5:

                    self.get_logger().warn(
                        "Rover position not available yet. "
                        "Skipping frame."
                    )

                return

            # ---------------------------------------------
            # Run YOLO
            # ---------------------------------------------

            results = self.model.predict(
                source=image,
                imgsz=320,
                conf=0.25,
                device="cpu",
                verbose=False
            )

            result = results[0]

            # ---------------------------------------------
            # Timestamp
            # ---------------------------------------------

            timestamp = (
                f"{msg.header.stamp.sec}."
                f"{msg.header.stamp.nanosec:09d}"
            )

            # ---------------------------------------------
            # Detection list
            # ---------------------------------------------

            detections = []

            # ---------------------------------------------
            # Process YOLO detections
            # ---------------------------------------------

            if result.boxes is not None:

                for box in result.boxes:

                    class_id = int(
                        box.cls[0].item()
                    )

                    confidence = float(
                        box.conf[0].item()
                    )

                    class_name = self.model.names[
                        class_id
                    ]

                    bbox = (
                        box.xyxy[0]
                        .cpu()
                        .numpy()
                        .tolist()
                    )

                    x1, y1, x2, y2 = bbox

                    detection = {
                        "class": class_name,
                        "confidence": round(
                            confidence,
                            4
                        ),
                        "bbox": [
                            round(x1, 2),
                            round(y1, 2),
                            round(x2, 2),
                            round(y2, 2)
                        ]
                    }

                    detections.append(
                        detection
                    )

                    # -------------------------------------
                    # Save detection to CSV
                    # -------------------------------------

                    with open(
                        self.csv_path,
                        "a",
                        newline=""
                    ) as file:

                        writer = csv.writer(file)

                        writer.writerow([
                            timestamp,
                            self.frame_count,
                            round(x, 3),
                            round(y, 3),
                            class_name,
                            round(confidence, 4),
                            round(x1, 2),
                            round(y1, 2),
                            round(x2, 2),
                            round(y2, 2),

                            (
                                ""
                                if self.soil_moisture is None
                                else round(
                                    self.soil_moisture,
                                    2
                                )
                            ),

                            (
                                ""
                                if self.temperature is None
                                else round(
                                    self.temperature,
                                    2
                                )
                            ),

                            (
                                ""
                                if self.humidity is None
                                else round(
                                    self.humidity,
                                    2
                                )
                            )
                        ])

                    self.detection_count += 1

            # ---------------------------------------------
            # Publish integrated detection message
            # ---------------------------------------------

            detection_message = String()

            detection_message.data = str({
                "timestamp": timestamp,
                "frame": self.frame_count,
                "x": round(x, 3),
                "y": round(y, 3),
                "soil_moisture": self.soil_moisture,
                "temperature": self.temperature,
                "humidity": self.humidity,
                "detections": detections
            })

            self.detection_publisher.publish(
                detection_message
            )

            # ---------------------------------------------
            # Processing time
            # ---------------------------------------------

            elapsed = time.time() - start_time

            # ---------------------------------------------
            # Safe sensor display
            # ---------------------------------------------

            soil_text = (
                "None"
                if self.soil_moisture is None
                else f"{self.soil_moisture:.2f}"
            )

            temp_text = (
                "None"
                if self.temperature is None
                else f"{self.temperature:.2f}"
            )

            humidity_text = (
                "None"
                if self.humidity is None
                else f"{self.humidity:.2f}"
            )

            # ---------------------------------------------
            # Console output
            # ---------------------------------------------

            self.get_logger().info(
                f"Frame {self.frame_count} | "
                f"Detections: {len(detections)} | "
                f"Position: ({x:.3f}, {y:.3f}) | "
                f"Soil: {soil_text} | "
                f"Temp: {temp_text} | "
                f"Humidity: {humidity_text} | "
                f"{elapsed * 1000:.1f} ms"
            )

        except Exception as e:

            self.get_logger().error(
                f"YOLO processing error: {e}"
            )

    # =====================================================
    # SHUTDOWN SUMMARY
    # =====================================================

    def print_summary(self):

        self.get_logger().info(
            "========================================"
        )

        self.get_logger().info(
            "YOLO DETECTOR SUMMARY"
        )

        self.get_logger().info(
            f"Frames received: {self.frame_count}"
        )

        self.get_logger().info(
            f"Frames skipped: {self.skipped_frames}"
        )

        self.get_logger().info(
            f"Total detections: {self.detection_count}"
        )

        self.get_logger().info(
            f"CSV file: {self.csv_path}"
        )

        self.get_logger().info(
            "========================================"
        )


# =========================================================
# MAIN
# =========================================================

def main(args=None):

    rclpy.init(args=args)

    node = YOLODetector()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        node.print_summary()

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":

    main()
