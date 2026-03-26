import pymysql
import pandas as pd
import numpy as np
import json

# 1. DB 연결 설정 (본인 비밀번호로 수정!)
conn = pymysql.connect(host='127.0.0.1', user='root', password='0000', database='rosdb', charset='utf8')

try:
    # 2. 데이터 불러오기
    print("📂 DB에서 데이터를 불러오는 중...")
    query = "SELECT ranges, action FROM lidardata"
    df_raw = pd.read_sql(query, conn)
    
    if df_raw.empty:
        print("❌ DB에 데이터가 없습니다! 거북이를 먼저 돌려주세요.")
    else:
        # 3. JSON 문자열을 실제 리스트로 변환
        print("⚙️ JSON 파싱 중...")
        df_raw['ranges'] = df_raw['ranges'].apply(json.loads)

        # 4. 360개 컬럼으로 확장 (이게 핵심!)
        # 리스트 형태의 컬럼을 분리하여 360개의 컬럼(0~359)을 가진 데이터프레임 생성
        lidar_columns = pd.DataFrame(df_raw['ranges'].tolist())
        
        # 컬럼 이름 예쁘게 붙이기 (dist_0, dist_1 ... dist_359)
        lidar_columns.columns = [f'dist_{i}' for i in range(360)]

        # 5. 주행 액션(Action) 컬럼 합치기
        final_df = pd.concat([lidar_columns, df_raw['action']], axis=1)

        # 6. 결과 확인
        print("\n✅ 변환 완료!")
        print(f"전체 데이터 모양: {final_df.shape}") # (데이터개수, 361)이 나와야 함
        print(final_df.head()) # 상위 5개 데이터 확인

        # 7. CSV 파일로 저장 (나중에 학습용으로 쓰기 좋음)
        final_df.to_csv("processed_lidar_data.csv", index=False)
        print("\n💾 'processed_lidar_data.csv'로 저장되었습니다.")

        # 8. 넘파이(NumPy) 형식으로도 변환해보기
        np_data = final_df.to_numpy()
        print(f"NumPy 배열 변환 성공! (크기: {np_data.shape})")

finally:
    conn.close()