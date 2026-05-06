"""
모든 시뮬레이션 실행 스크립트
"""

import attendance_utility
import memory_activation_semester
import team_decision_wm


def main():
    print("=" * 70)
    print("  강의계획서 메타분석 - 정량 모델링 시뮬레이션")
    print("=" * 70)

    print("\n[1/3] 출석 행동 Utility 시뮬레이션")
    attendance_utility.plot_utility_comparison()

    print("\n[2/3] 학기별 Memory Activation 시뮬레이션")
    memory_activation_semester.plot_activation_curves()

    print("\n[3/3] 팀 구성 의사결정 시뮬레이션")
    team_decision_wm.plot_team_decision()

    print("\n" + "=" * 70)
    print("  완료. figures/ 폴더 확인.")
    print("=" * 70)


if __name__ == '__main__':
    main()
