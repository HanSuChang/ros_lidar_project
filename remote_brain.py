import roslibpy
import pymysql
import json
import time
import random

# DB 설정 (본인 비밀번호로 수정하세요!)
conn = pymysql.connect(host='127.0.0.1', user='root', password='0000', database='rosdb', charset='utf8')
cursor = conn.cursor()
client = roslibpy.Ros(host='localhost', port=9090)

def start_listening():
    print("🔥 2초 박자 폭주 시스템 가동!")
    listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
    publisher = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')

    def callback(message):
        ranges = message['ranges']
        
        # 정면/왼쪽/오른쪽 평균 거리 계산
        front_dist = sum(ranges[350:360] + ranges[0:11]) / 21
        left_dist  = sum(ranges[80:101]) / 21
        right_dist = sum(ranges[260:281]) / 21

        move_cmd = {'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}

        # --- 맵을 휘젓기 위한 무대뽀 로직 ---
        if front_dist < 1.0: 
            # 벽을 만나면 제자리에서 아주 크게 돕니다 (회전속도 4.0)
            move_cmd['angular']['z'] = 4.0 if left_dist > right_dist else -4.0
            action = "BIG_TURN"
        else:
            # 앞이 비었으면 아주 빠르게 전진합니다 (속도 4.0)
            # 이때도 지그재그를 위해 랜덤하게 회전값을 섞습니다.
            move_cmd['linear']['x'] = 4.0 
            move_cmd['angular']['z'] = random.uniform(-2.5, 2.5)
            action = "FAST_ZIGZAG"

        publisher.publish(roslibpy.Message(move_cmd))
        
        # DB 저장
        try:
            sql = "INSERT INTO lidardata (ranges, action) VALUES (%s, %s)"
            cursor.execute(sql, (json.dumps(ranges), action))
            conn.commit()
            print(f"[{time.strftime('%H:%M:%S')}] {action} 실행완료 (2초 주기)")
        except:
            pass

    listener.subscribe(callback)

client.on_ready(start_listening)
client.run_forever()