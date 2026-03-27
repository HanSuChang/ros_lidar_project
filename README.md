 LIDAR_MOCK: ROS2 & Data Pipeline Project

> LiDAR 모의 데이터를 생성하고, ROS2 환경에서 주행 액션을 결정한 뒤  
> MySQL DB에 적재하여 AI 학습용 데이터셋(361 columns)으로 가공하는 전체 파이프라인 프로젝트

---

 📁 주요 파일 구성 및 역할

## 1. Data Generation & ROS2 Communication

| 파일 | 설명 |
|------|------|
| `lidar_simulation.py` / `lidar_pub.py` / `lidar_publisher.py` | 2초 주기로 360도 랜덤 LiDAR 거리 데이터를 생성하여 토픽 발행 |
| `lidar_standalone.py` | 의존성 없이 독립적으로 LiDAR 데이터 생성을 테스트하는 스크립트 |
| `remote_brain.py` | roslibpy를 이용해 원격에서 토픽을 수신하고 주행 액션(직진/좌회전/우회전 등)을 결정하여 turtlesim 제어 명령 전송 |

## 2. Database Management (MySQL)

| 파일 | 설명 |
|------|------|
| `db_uploader.py` | LiDAR ranges[] 데이터(JSON)와 결정된 action을 MySQL `lidardata` 테이블에 실시간 INSERT |
| `setup.py` | MySQL 스키마 생성 및 초기 테이블 환경 설정 |

## 3. Data Processing & Export

| 파일 | 설명 |
|------|------|
| `db_processor.py` | DB에 저장된 JSON 데이터를 불러와 전처리 로직 실행 |
| `preprocess_data.py` | JSON 문자열을 파싱하여 360개 거리 값 컬럼 + 1개 액션 컬럼(총 361개)으로 변환 |
| `db_to_csv.py` | 가공된 데이터를 CSV 형식으로 내보내기 |
| `processed_lidar_data.csv` / `final_lidar_dataset.csv` | 전처리 완료된 최종 데이터셋 파일 |

---

##  전체 파이프라인 흐름

LiDAR 데이터 생성 → ROS2 토픽 발행 → 주행 액션 결정

       ↓
       
  MySQL DB 적재
  
       ↓
  JSON 전처리 → 361 Column CSV 변환 → AI 학습 데이터셋




##  업데이트 내역

### 2026-03-26 — Git 형상 관리 및 파이프라인 안정화 완료

- 모듈화 완료: 단일 스크립트에서 관리하던 로직을 `publisher`, `brain`, `uploader`, `processor`로 분리하여 유지보수성 향상
- Git 동기화: `.gitignore` 적용으로 불필요한 캐시 파일 제외, 핵심 소스 코드 및 데이터셋 GitHub 푸시 완료
- 데이터 무결성 확보: DB → CSV 변환 시 데이터 누락 없이 361개 피처가 정확하게 매핑되도록 로직 수정


## 🛠 기술 스택

| 분류 | 사용 기술 |
|------|-----------|
| Language | Python 3.10 |
| Framework | ROS2 (Humble), roslibpy |
| Database | MySQL (JSON Type Storage) |
| Data Science | Pandas, NumPy |
