3월 26일걸로 봐주세요!

(ros_lidar_project)

2026. 03. 26

1. 벽 충돌 방지 및 LiDAR 로직 개선
Obstacle Detection Fix: LiDAR 데이터가 벽을 제대로 인식하지 못해 발생하던 충돌 문제를 해결했습니다.

Scan Data Processing: 특정 각도 범위 내의 최소 거리를 실시간으로 체크하여, 벽과의 거리가 임계치 이하일 때 즉시 정지 및 회피 기동을 수행하도록 수정했습니다.

Stability Improvement: 센서 데이터의 노이즈를 필터링하여 급발진이나 인식 오류를 최소화했습니다.

2. Git 레포지토리 구축 및 동기화 완료
로컬 작업물을 원격 저장소(https://github.com/HanSuChang/ros_lidar_project)에 성공적으로 푸시하여 협업 및 백업 환경을 구축했습니다.

.gitignore 설정을 통해 build, install, log 등 불필요한 ROS2 빌드 파일을 제외하고 순수 소스 코드만 깔끔하게 관리하도록 설정했습니다.

개발 환경
OS: Ubuntu 22.04 LTS

ROS Version: ROS2 Humble

Platform: TurtleBot3 (Waffle Pi / Burger)

Language: Python 3.10 / C++

실행 방법
패키지를 빌드하고 실행하려면 아래 명령어를 사용하세요.

Bash
# 워크스페이스 빌드 및 소싱
cd ~/ros2_ws
colcon build --packages-select ros_lidar_project
source install/setup.bash

# 메인 노드 실행 (LiDAR 장애물 회피)
ros2 run ros_lidar_project [실행파일_이름]
📂 주요 파일 구조
[파일명].py: LiDAR 스캔 데이터를 분석하고 cmd_vel을 제어하는 메인 로직

README.md: 프로젝트 개요 및 업데이트 기록 (현재 파일)
