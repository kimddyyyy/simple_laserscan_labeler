#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import os
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy
from sensor_msgs.msg import LaserScan


class LaserScanToTextConverter(Node):
    def __init__(self, qos_profile):
        super().__init__('txt_converter')

        self.sequence_name = "1"
        self.save_dir = "./" + self.sequence_name
        self.scan_topic = "/scan_raw"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        self.cnt = 0

        self.scan_sub = self.create_subscription(LaserScan, self.scan_topic, self.scan_callback, qos_profile)

    def scan_callback(self, msg):
        num_ranges = len(msg.ranges)

        scan_data = []

        for i in range(num_ranges):
            r = msg.ranges[i]
            t = msg.angle_min + i * msg.angle_increment
            x = r * math.cos(t)
            y = r * math.sin(t)

            # 데이터 순서: i, r, t, x, y, 0 (l)
            scan_data.append(f"{i}, {r}, {t}, {x}, {y}, 0\n")

        file_name = f"scan_{self.cnt:04d}.txt"
        file_path = os.path.join(self.save_dir, file_name)

        with open(file_path, 'w') as file:
            file.writelines(scan_data)

        self.get_logger().info(f"Saved scan {self.cnt} to {file_path}")

        self.cnt += 1


def main(args=None):
    rclpy.init(args=args)

    qos_profile = QoSProfile(
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=100,
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.VOLATILE
    )

    txt_converter = LaserScanToTextConverter(qos_profile)

    try:
        rclpy.spin(txt_converter)
    except KeyboardInterrupt:
        pass

    txt_converter.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

