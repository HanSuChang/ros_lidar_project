import roslibpy
import pymysql
import json
import time

# --- 1. DB 및 ROS 연결 설정 ---
# 비밀번호 '0000' 확인!
conn = pymysql.connect(host='localhost', user='root', password='0000', database='rosdb', charset='utf8')
cursor = conn.cursor()
client = roslibpy.Ros(host='localhost', port=9090)

def start_listening():
    # 이 글자가 터미널에 찍혀야 성공입니다!
    print("시스템 가동! 거북이 부드러운 조종을 시작합니다.")
    
    listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
    publisher = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')

    def callback(message):
        ranges = message['ranges']
        
        # 1. 센서 데이터 가공
        front_dist = sum(ranges[0:15] + ranges[345:360]) / 30
        left_dist = sum(ranges[80:100]) / 20
        right_dist = sum(ranges[260:280]) / 20

        # 2. 부드러운 주행 로직
        max_linear_speed = 2.0 
        min_safe_dist = 0.5    
        move_cmd = {'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}

        if front_dist > min_safe_dist:
            move_cmd['linear']['x'] = min(max_linear_speed, front_dist * 0.4)
            action = f"FWD_{move_cmd['linear']['x']:.2f}"
        else:
            if left_dist > right_dist:
                move_cmd['angular']['z'] = 1.5
                action = "TURN LEFT"
            else:
                move_cmd['angular']['z'] = -1.5
                action = "TURN RIGHT"

        # 3. 명령 발행 및 DB 저장
        publisher.publish(roslibpy.Message(move_cmd))
        try:
            sql = "INSERT INTO lidardata (ranges, action) VALUES (%s, %s)"
            cursor.execute(sql, (json.dumps(ranges), action))
            conn.commit()
            print(f"[{time.strftime('%H:%M:%S')}] {action} | F:{front_dist:.2f}m")
        except Exception as e:
            print(f"DB 저장 에러: {e}")

    listener.subscribe(callback)

# 이 아랫부분이 있어야 프로그램이 죽지 않고 계속 돌아갑니다!
client.on_ready(start_listening)

try:
    client.run_forever()
except KeyboardInterrupt:
    print("\n시스템 종료")
    cursor.close()
    conn.close()
    client.terminate()