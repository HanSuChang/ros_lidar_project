import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import random
import math

class LidarMockPublisher(Node):
    def __init__(self):
        super().__init__('lidar_mock_node')
        self.publisher_ = self.create_publisher(LaserScan, '/scan', 10)
        # --- 핵심: 정확히 2.0초 주기로 발행 ---
        self.timer = self.create_timer(2.0, self.publish_random_scan)
        self.get_logger().info('🐢 2초 박자 랜덤 센서 가동!')

    def publish_random_scan(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser_frame'
        msg.angle_min = 0.0
        msg.angle_max = math.radians(359)
        msg.angle_increment = math.radians(1)
        msg.range_min = 0.12
        msg.range_max = 3.5

        ranges = [3.5] * 360
        # 맵을 휘젓기 위해 '직진'보다는 '벽'이 나타날 확률을 높였습니다.
        pattern = random.choice(["front_wall", "left_wall", "right_wall", "front_wall"])
        
        if pattern == "front_wall":
            for i in range(340, 360): ranges[i] = 0.3
            for i in range(0, 21): ranges[i] = 0.3
        elif pattern == "left_wall":
            for i in range(70, 111): ranges[i] = 0.3
        elif pattern == "right_wall":
            for i in range(250, 291): ranges[i] = 0.3

        msg.ranges = ranges
        self.publisher_.publish(msg)
        self.get_logger().info(f'📡 [2초 경과] 가짜 벽 생성: {pattern}')

def main(args=None):
    rclpy.init(args=args)
    node = LidarMockPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()