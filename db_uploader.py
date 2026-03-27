import pymysql
import json
import os

# 1. MySQL 연결 설정
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='0000',  # <--- 본인 MySQL 비밀번호로 수정!
    database='rosdb',
    charset='utf8'
)
cursor = conn.cursor()

# 2. 데이터셋 폴더 경로
DATASET_DIR = "lds02_dataset"
# 폴더 내 모든 .json 파일 목록 가져오기
files = [f for f in os.listdir(DATASET_DIR) if f.endswith('.json')]

print(f"총 {len(files)}개의 데이터를 DB로 업로드합니다...")

try:
    for filename in files:
        file_path = os.path.join(DATASET_DIR, filename)
        
        # JSON 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 데이터 추출 (ranges 배열을 문자열로 변환)
        ranges_json = json.dumps(data['ranges'])
        action = data['action']
        
        # SQL 실행
        sql = "INSERT INTO lidardata (ranges, action) VALUES (%s, %s)"
        cursor.execute(sql, (ranges_json, action))

    # 데이터 확정 (Commit)
    conn.commit()
    print("✅ 모든 데이터 업로드 완료!")

except Exception as e:
    print(f"❌ 에러 발생: {e}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()