import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math
import random

class LidarMockPublisher(Node):
    def __init__(self):
        super().__init__('lidar_pub_node')
        # /scan 토픽으로 데이터를 보낼 준비를 합니다.
        self.publisher_ = self.create_publisher(LaserScan, '/scan', 10)
        # 2초마다 토픽을 쏘는 타이머를 설정합니다.
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.get_logger().info('Lidar Pub Node가 시작되었습니다!')

    def timer_callback(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser'
        
        # LDS-02 설정값
        msg.angle_min = 0.0
        msg.angle_max = math.radians(359)
        msg.angle_increment = math.radians(1.0)
        msg.range_min = 0.12
        msg.range_max = 3.5
        
        # 랜덤하게 장애물 상황 만들기
        ranges = [3.5] * 360
        pattern = random.choice(['front', 'left', 'right', 'clear', 'clear', 'clear'])
        
        if pattern == 'front':
            for i in range(350, 360): ranges[i] = 0.4
            for i in range(0, 10): ranges[i] = 0.4
        elif pattern == 'left':
            for i in range(80, 100): ranges[i] = 0.4
        elif pattern == 'right':
            for i in range(260, 280): ranges[i] = 0.4

        msg.ranges = ranges
        self.publisher_.publish(msg)
        self.get_logger().info(f'데이터 발행 중... 패턴: {pattern}')

def main(args=None):
    rclpy.init(args=args)
    node = LidarMockPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()