import pymysql
import json
import pandas as pd

# 1. DB 연결
conn = pymysql.connect(host='localhost', user='root', password='0000', database='rosdb', charset='utf8')

# 2. 데이터 불러오기
print("데이터를 불러오는 중...")
df_raw = pd.read_sql("SELECT ranges, action FROM lidardata", conn)

# 3. 361개 컬럼으로 파싱 (리스트를 컬럼으로 펼치기)
# json.loads를 통해 문자열을 리스트로 복원한 뒤 DataFrame으로 만듭니다.
print("361개 컬럼으로 변환 중... 잠시만 기다려주세요.")
ranges_df = pd.DataFrame([json.loads(r) for r in df_raw['ranges']])
ranges_df['action'] = df_raw['action']

# 4. 결과 확인 및 저장
print(ranges_df.head())
ranges_df.to_csv('final_lidar_dataset.csv', index=False)

print(f"✅ 파싱 완료! 총 {len(ranges_df)}개의 데이터가 'final_lidar_dataset.csv'로 저장되었습니다.")
conn.close()