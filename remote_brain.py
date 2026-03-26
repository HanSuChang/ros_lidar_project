import roslibpy
import time

# 1. ROS Bridge 서버 연결
client = roslibpy.Ros(host='localhost', port=9090)

def start_listening():
    print("연결 성공! 거북이 조종을 시작합니다.")
    
    # [수신] /scan 토픽 구독
    listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
    # [발행] /turtle1/cmd_vel 토픽으로 명령 보낼 준비
    publisher = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')

    def callback(message):
        ranges = message['ranges']
        
        # 주행 판단 로직
        front_dist = sum(ranges[0:10] + ranges[350:360]) / 20
        left_dist = sum(ranges[80:100]) / 20
        right_dist = sum(ranges[260:280]) / 20

        # 거북이에게 보낼 속도 메시지 구조
        move_cmd = {
            'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
        }

        if front_dist < 0.6:
            # 장애물 발견 시 회전
            if left_dist > right_dist:
                action = "TURN LEFT"
                move_cmd['angular']['z'] = 2.0  # 왼쪽으로 회전
            else:
                action = "TURN RIGHT"
                move_cmd['angular']['z'] = -2.0 # 오른쪽으로 회전
        else:
            # 길 비었으면 직진
            action = "GO FORWARD"
            move_cmd['linear']['x'] = 2.0 # 앞으로 전진

        # 실제로 명령 발행(Publish)
        publisher.publish(roslibpy.Message(move_cmd))
        print(f"[{time.strftime('%H:%M:%S')}] Front: {front_dist:.2f}m | Action: {action}")

    listener.subscribe(callback)

client.on_ready(start_listening)

try:
    client.run_forever()
except KeyboardInterrupt:
    client.terminate()