LIDAR_MOCK: ROS2 & Data Project
본 프로젝트는 LiDAR 모의 데이터를 생성하여 ROS2 환경에서 주행 액션을 결정하고, 이를 MySQL DB에 적재한 뒤 AI 학습용 데이터셋(361 Column)으로 가공하는 전체 파이프라인을 포함합니다.

주요 파일 구성 및 역할
보내주신 프로젝트 구조에 따른 각 파일의 상세 기능입니다.

1. Data Generation & ROS2 Communication
lidar_simulation.py / lidar_pub.py / lidar_publisher.py: 2초 주기로 360도의 랜덤 LiDAR 거리 데이터를 생성하여 토픽을 발행합니다.

lidar_standalone.py: 의존성 없이 독립적으로 LiDAR 데이터 생성을 테스트하기 위한 스크립트입니다.

remote_brain.py: roslibpy를 이용해 원격에서 토픽을 수신하고, 주행 액션(직진/좌회전/우회전 등)을 결정하여 거북이(turtlesim) 제어 명령을 보냅니다.

2. Database Management (MySQL)
db_uploader.py: 수집된 LiDAR ranges[] 데이터(JSON 형식)와 결정된 action을 MySQL 서버의 lidardata 테이블에 실시간으로 INSERT 합니다.

setup.py: MySQL 스키마 생성 및 초기 테이블 환경 설정을 담당합니다.

3. Data Processing & Export
db_processor.py: DB에 저장된 JSON 타입의 데이터를 불러와 전처리 로직을 실행합니다.

preprocess_data.py: JSON 문자열을 파싱하여 **360개의 거리 값 컬럼과 1개의 액션 컬럼(총 361개)**으로 변환합니다.

db_to_csv.py: 가공된 데이터를 최종적으로 분석 및 학습에 용이한 CSV 형식으로 내보냅니다.

processed_lidar_data.csv / final_lidar_dataset.csv: 모든 전처리가 완료된 최종 데이터셋 파일입니다.

2026. 03. 26 업데이트 사항
"Git 형상 관리 및 파이프라인 안정화 완료"

모듈화 완료: 단일 스크립트에서 관리하던 로직을 publisher, brain, uploader, processor로 분리하여 유지보수성을 높였습니다.

Git 동기화: .gitignore를 적용하여 불필요한 캐시 파일을 제외하고 핵심 소스 코드와 데이터셋을 성공적으로 GitHub에 푸시했습니다.

데이터 무결성 확보: DB에서 CSV로 변환 시 데이터 누락 없이 361개의 피처가 정확하게 매핑되도록 로직을 수정했습니다.

기술 스택
Language: Python 3.10

Framework: ROS2 (Humble), roslibpy

Database: MySQL (JSON Type Storage)

Data Science: Pandas, Numpy
