import json
import math
import os
import random
import numpy as np

# --- 1. 환경 설정 ---
ANGLE_MIN_DEG = 0
ANGLE_MAX_DEG = 359
NUM_POINTS = 360
RANGE_MIN = 0.12 
RANGE_MAX = 3.5 
SAFE_DIST = 0.5 
DATASET_DIR = "lds02_dataset" # 데이터가 저장될 폴더 이름

# --- 2. 함수 정의 (기존과 동일) ---
def create_empty_scan():
    ranges = [float(RANGE_MAX) for _ in range(NUM_POINTS)]
    intensities = [100.0 for _ in range(NUM_POINTS)]
    return {"ranges": ranges, "intensities": intensities}

def make_the_wall(ranges, center_deg, width_deg):
    half_width = width_deg // 2
    for offset in range(-half_width, half_width + 1):
        idx = (center_deg + offset) % NUM_POINTS
        ranges[idx] = 0.4

def generate_single_scan(pattern_name):
    scan = create_empty_scan()
    if pattern_name == "front_wall":
        make_the_wall(scan["ranges"], center_deg=0, width_deg=40)
    elif pattern_name == "left_wall":
        make_the_wall(scan["ranges"], center_deg=90, width_deg=30)
    elif pattern_name == "right_wall":
        make_the_wall(scan["ranges"], center_deg=270, width_deg=30)
    return scan

def decide_action(scan_data):
    ranges = np.array(scan_data["ranges"])
    front = np.r_[ranges[350:360], ranges[0:10]]
    left  = ranges[80:100]
    right = ranges[260:280]

    front_dist = np.mean(front)
    left_dist  = np.mean(left)
    right_dist = np.mean(right)

    if front_dist < SAFE_DIST:
        action = "turn_left" if left_dist > right_dist else "turn_right"
    else:
        action = "go_forward"
    return action

# --- 3. 데이터셋 생성 및 저장 로직 ---
if __name__ == "__main__":
    # 데이터 저장 폴더 만들기
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    AVAILABLE_PATTERNS = ["front_wall", "left_wall", "right_wall", "clear_path"]
    NUM_SAMPLES = 1000 # 만들 데이터 개수

    print(f"{NUM_SAMPLES}개의 데이터를 생성하여 {DATASET_DIR} 폴더에 저장합니다...")

    for i in range(NUM_SAMPLES):
        pattern = random.choice(AVAILABLE_PATTERNS)
        
        # 1. 스캔 데이터 생성
        if pattern == "clear_path":
            scan = create_empty_scan()
        else:
            scan = generate_single_scan(pattern)
        
        # 2. 주행 액션 결정
        action = decide_action(scan)
        
        # 3. 데이터 합치기 (메타데이터 추가)
        scan["action"] = action
        scan["pattern"] = pattern
        
        # 4. JSON 파일로 저장
        filename = os.path.join(DATASET_DIR, f"scan_data_{i:04d}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(scan, f, indent=2)

    print("데이터셋 생성 완료!")