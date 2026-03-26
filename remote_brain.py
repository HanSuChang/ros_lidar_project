import roslibpy
import pymysql
import json
import time

# --- 1. DB 및 ROS 연결 설정 ---
conn = pymysql.connect(host='localhost', user='root', password='0000', database='rosdb', charset='utf8')
cursor = conn.cursor()
client = roslibpy.Ros(host='localhost', port=9090)

def start_listening():
    print("시스템 가동! 거북이 조종 및 데이터 저장을 시작합니다.")
    
    listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
    publisher = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')

    def callback(message):
        ranges = message['ranges']
        
        # [판단 로직] 정면/왼쪽/오른쪽 평균 거리 계산
        front_dist = sum(ranges[0:15] + ranges[345:360]) / 30
        left_dist = sum(ranges[80:100]) / 20
        right_dist = sum(ranges[260:280]) / 20

        move_cmd = {'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}

        # [주행 결정]
        if front_dist < 0.6:
            if left_dist > right_dist:
                action, move_cmd['angular']['z'] = "turn_left", 2.0
            else:
                action, move_cmd['angular']['z'] = "turn_right", -2.0
        else:
            action, move_cmd['linear']['x'] = "go_forward", 2.0

        # [A. 거북이 조종]
        publisher.publish(roslibpy.Message(move_cmd))

        # [B. MySQL 실시간 저장]
        try:
            sql = "INSERT INTO lidardata (ranges, action) VALUES (%s, %s)"
            cursor.execute(sql, (json.dumps(ranges), action))
            conn.commit() # 이 줄이 있어야 진짜로 저장됩니다!
            print(f"[{time.strftime('%H:%M:%S')}] {action} -> DB 저장 완료")
        except Exception as e:
            print(f"DB 저장 에러: {e}")

    listener.subscribe(callback)

client.on_ready(start_listening)

try:
    client.run_forever()
except KeyboardInterrupt:
    cursor.close()
    conn.close()
    client.terminate()