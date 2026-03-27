import roslibpy
import pymysql
import json
import time
import math
import random

# ──────────────────────────────────────────
# 설정값
# ──────────────────────────────────────────
RANGE_MIN   = 0.12  # LDS-02 최소 신뢰 거리 (m)
RANGE_MAX   = 3.5   # LDS-02 최대 신뢰 거리 (m)

FRONT_SAFE  = 1.0   # 정면 안전거리
SIDE_SAFE   = 0.35  # 좌우 안전거리
DIAG_SAFE   = 0.6   # 대각선 안전거리

LINEAR_SPD  = 1.2   # 전진 속도
TURN_SPD    = 1.5   # 회전 속도

# turn 방향 기억용 (좌우가 비슷할 때 같은 방향 유지)
last_turn_dir = 1  # 1 = 왼쪽, -1 = 오른쪽

# ──────────────────────────────────────────
# 유효값 필터링 함수
# ──────────────────────────────────────────
def filtered_mean(ranges, start_idx, end_idx):
    samples = ranges[start_idx:end_idx]
    valid = [
        r for r in samples
        if not math.isnan(r) and not math.isinf(r)
        and RANGE_MIN <= r <= RANGE_MAX
    ]
    if len(valid) == 0:
        return RANGE_MAX
    return sum(valid) / len(valid)

# ──────────────────────────────────────────
# 회전 방향 결정 함수
# 좌우 차이가 0.3m 이상일 때만 방향 바꿈
# 그 이하면 마지막 방향 유지 → turn_right 쏠림 방지
# ──────────────────────────────────────────
def decide_turn_dir(left_dist, right_dist):
    global last_turn_dir
    diff = left_dist - right_dist  # 양수면 왼쪽이 더 여유
    if abs(diff) > 0.3:
        last_turn_dir = 1 if diff > 0 else -1
    # 차이가 작으면 last_turn_dir 유지 (한쪽으로 쏠리지 않음)
    return last_turn_dir

# ──────────────────────────────────────────
# DB 연결
# ──────────────────────────────────────────
conn   = pymysql.connect(host='127.0.0.1', user='root', password='0000',
                         database='rosdb', charset='utf8')
cursor = conn.cursor()

client = roslibpy.Ros(host='localhost', port=9090)

def start_listening():
    print("🟢 최종 주행 시스템 가동!")
    print(f"   유효 거리 범위: {RANGE_MIN}m ~ {RANGE_MAX}m")

    listener  = roslibpy.Topic(client, '/scan',            'sensor_msgs/LaserScan')
    publisher = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')

    def callback(message):
        ranges = message['ranges']

        # ── 각 방향 유효값 평균 계산 ─────────────────────────────
        front_dist       = (filtered_mean(ranges, 350, 360) * 10
                          + filtered_mean(ranges, 0,   10)  * 10) / 20
        front_left_dist  = filtered_mean(ranges, 15,  45)
        front_right_dist = filtered_mean(ranges, 315, 345)
        left_dist        = filtered_mean(ranges, 80,  120)
        right_dist       = filtered_mean(ranges, 250, 290)

        # ── 복도 판단 ─────────────────────────────────────────────
        is_corridor = (left_dist  < SIDE_SAFE and
                       right_dist < SIDE_SAFE and
                       front_dist > FRONT_SAFE)

        move_cmd = {
            'linear':  {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
        }

        # ── 주행 판단 ─────────────────────────────────────────────

        if is_corridor:
            # 복도: 양옆 좁고 정면 뚫림 → 완전 일직선
            move_cmd['linear']['x']  = LINEAR_SPD
            move_cmd['angular']['z'] = 0.0
            action = "go_corridor"

        elif front_dist < FRONT_SAFE:
            # 정면 장애물 → 제자리 회전
            turn_dir = decide_turn_dir(left_dist, right_dist)
            move_cmd['angular']['z'] = TURN_SPD * turn_dir
            action = "turn_left" if turn_dir == 1 else "turn_right"

        elif front_right_dist < DIAG_SAFE and front_left_dist < DIAG_SAFE:
            # 양쪽 대각 다 막힘 → 코너
            turn_dir = decide_turn_dir(left_dist, right_dist)
            move_cmd['angular']['z'] = TURN_SPD * turn_dir
            action = "corner_turn_left" if turn_dir == 1 else "corner_turn_right"

        elif front_right_dist < DIAG_SAFE:
            # 우전방 막힘 → 왼쪽으로 틀며 전진
            move_cmd['linear']['x']  = LINEAR_SPD * 0.6
            move_cmd['angular']['z'] = TURN_SPD * 0.8
            action = "avoid_front_right"

        elif front_left_dist < DIAG_SAFE:
            # 좌전방 막힘 → 오른쪽으로 틀며 전진
            move_cmd['linear']['x']  = LINEAR_SPD * 0.6
            move_cmd['angular']['z'] = -TURN_SPD * 0.8
            action = "avoid_front_left"

        elif right_dist < SIDE_SAFE:
            # 오른쪽 벽 → 왼쪽으로 살짝 틀며 전진
            move_cmd['linear']['x']  = LINEAR_SPD * 0.8
            move_cmd['angular']['z'] = TURN_SPD * 0.5
            action = "avoid_right_wall"

        elif left_dist < SIDE_SAFE:
            # 왼쪽 벽 → 오른쪽으로 살짝 틀며 전진
            move_cmd['linear']['x']  = LINEAR_SPD * 0.8
            move_cmd['angular']['z'] = -TURN_SPD * 0.5
            action = "avoid_left_wall"

        else:
            # 사방 여유 → 완전 일직선 직진
            move_cmd['linear']['x']  = LINEAR_SPD
            move_cmd['angular']['z'] = 0.0
            action = "go_forward"

        publisher.publish(roslibpy.Message(move_cmd))

        # ── DB 저장 ───────────────────────────────────────────────
        try:
            sql = "INSERT INTO lidardata (ranges, action) VALUES (%s, %s)"
            cursor.execute(sql, (json.dumps(ranges), action))
            conn.commit()
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"front={front_dist:.2f}  "
                  f"fl={front_left_dist:.2f}  fr={front_right_dist:.2f}  "
                  f"left={left_dist:.2f}  right={right_dist:.2f}  "
                  f"→ {action}")
        except Exception as e:
            print(f"DB 저장 실패: {e}")

    listener.subscribe(callback)

client.on_ready(start_listening)
client.run_forever()