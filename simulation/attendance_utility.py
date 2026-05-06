"""
시뮬레이션 1: 출석 행동의 Utility 곡선
========================================
수업 공식: U(n) = U(n-1) + α[R(n) - U(n-1)]

세 가지 출석 체크 시나리오에서 학생의 "출석 행동" utility 변화를 시뮬레이션한다.
- 시나리오 A: 고정 일정 (매주 월요일에만 체크)
- 시나리오 B: 랜덤 균등 (학기당 7회 무작위)
- 시나리오 C: 랜덤 + 빈도 비공개 (본 강의 방식)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── 파라미터 ─────────────────────────────────
ALPHA = 0.15            # 학습률
N_CLASSES = 30          # 학기 총 수업 횟수 (15주 × 주 2회)
N_CHECKS = 7            # 학기당 출석 체크 횟수
SEED = 42

# 보상 매트릭스
R_ATTEND_CHECK = 1.0       # 출석 + 체크 발생 → 페널티 회피
R_ATTEND_NOCHECK = 0.1     # 출석 + 체크 없음 → 미세 학습 보상
R_ABSENT_CHECK = -3.0      # 불참 + 체크 발생 → 출석점수 손실
R_ABSENT_NOCHECK = 0.0     # 불참 + 체크 없음 → 비용 없음


def simulate_attendance(scenario: str, n_classes: int = N_CLASSES,
                        alpha: float = ALPHA, seed: int = SEED) -> dict:
    """
    학생의 출석 행동 utility 변화 시뮬레이션.
    학생은 utility가 낮으면 불참 확률 증가 (logistic).
    """
    rng = np.random.default_rng(seed)

    # 출석 체크 일정 결정
    if scenario == 'fixed':
        # 매주 월요일(짝수 인덱스)만 체크
        check_days = [i for i in range(0, n_classes, 2)][:N_CHECKS]
    elif scenario == 'random_known':
        # 랜덤이지만 횟수는 알려짐 → 학생이 확률 계산 가능
        check_days = sorted(rng.choice(n_classes, N_CHECKS, replace=False).tolist())
    elif scenario == 'random_hidden':
        # 랜덤 + 학생은 횟수도 모름
        check_days = sorted(rng.choice(n_classes, N_CHECKS, replace=False).tolist())
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    U = [0.5]            # 초기 utility (중립)
    attendance = []      # 1=출석, 0=불참
    rewards = []
    learned_pattern = 0  # 시나리오 A에서 패턴 학습 정도

    for day in range(n_classes):
        # 출석 결정: utility가 높을수록 출석 확률 ↑
        # 시나리오 A는 후반에 패턴 학습 → 화요일에 의도적 결석
        if scenario == 'fixed' and day > 6 and day % 2 == 1:
            # 화요일은 체크 없음을 학습 → 결석 유인
            p_attend = 1 / (1 + np.exp(-3 * (U[-1] - 0.5)))  # 정상보다 낮은 확률
            p_attend *= 0.6  # 패턴 학습으로 결석 강화
        else:
            p_attend = 1 / (1 + np.exp(-4 * (U[-1] - 0.3)))

        attended = rng.random() < p_attend
        attendance.append(int(attended))

        # 체크 발생 여부
        check_today = day in check_days

        # 보상 결정
        if attended and check_today:
            R = R_ATTEND_CHECK
        elif attended and not check_today:
            R = R_ATTEND_NOCHECK
        elif not attended and check_today:
            R = R_ABSENT_CHECK
        else:
            R = R_ABSENT_NOCHECK

        rewards.append(R)

        # Utility 갱신 (수업 공식)
        U_new = U[-1] + alpha * (R - U[-1])
        U.append(U_new)

    return {
        'utilities': np.array(U),
        'attendance': np.array(attendance),
        'rewards': np.array(rewards),
        'check_days': check_days,
        'scenario': scenario,
        'attendance_rate': np.mean(attendance)
    }


def plot_utility_comparison(save: bool = True):
    """세 시나리오 utility 곡선 비교."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                             gridspec_kw={'height_ratios': [3, 1]})

    scenarios = {
        '고정 일정 (매주 월)':       ('fixed', '#3498DB'),
        '랜덤 균등 (횟수 공개)':     ('random_known', '#F39C12'),
        '랜덤 + 빈도 비공개 (본 강의)': ('random_hidden', '#E74C3C'),
    }

    results = {}
    for label, (key, color) in scenarios.items():
        result = simulate_attendance(key)
        results[label] = (result, color)

        x = np.arange(len(result['utilities']))
        axes[0].plot(x, result['utilities'], label=label, color=color,
                     linewidth=1.8, alpha=0.85)

    axes[0].axhline(y=0.5, color='gray', linestyle='--', alpha=0.4)
    axes[0].set_ylabel('출석 행동 Utility $U(n)$', fontsize=11)
    axes[0].set_title('출석 체크 방식별 학생 utility 변화 (수업 공식: $U(n)=U(n-1)+\\alpha[R(n)-U(n-1)]$)',
                      fontsize=12, fontweight='bold')
    axes[0].legend(loc='lower left', fontsize=10)
    axes[0].grid(alpha=0.3)
    axes[0].set_ylim(-0.5, 1.1)

    # 출석률 막대
    labels = list(results.keys())
    rates = [r['attendance_rate'] * 100 for r, _ in results.values()]
    colors = [c for _, c in results.values()]
    axes[1].barh(labels, rates, color=colors, alpha=0.7)
    for i, (rate, color) in enumerate(zip(rates, colors)):
        axes[1].text(rate + 1, i, f'{rate:.1f}%', va='center', fontsize=10)
    axes[1].set_xlabel('학기 평균 출석률 (%)', fontsize=11)
    axes[1].set_xlim(0, 110)
    axes[1].grid(alpha=0.3, axis='x')

    plt.xlabel('수업 회차 (15주 × 주 2회 = 30회)', fontsize=11)
    plt.tight_layout()

    if save:
        path = os.path.join(FIGURES_DIR, 'sim1_attendance_utility.png')
        plt.savefig(path, dpi=200, bbox_inches='tight')
        print(f"[저장] {path}")

    plt.close()
    return results


if __name__ == '__main__':
    print("=" * 60)
    print("시뮬레이션 1: 출석 행동 Utility")
    print("=" * 60)

    results = plot_utility_comparison()

    print("\n── 결과 요약 ──")
    for label, (result, _) in results.items():
        print(f"\n{label}:")
        print(f"  최종 utility: {result['utilities'][-1]:.3f}")
        print(f"  출석률: {result['attendance_rate']*100:.1f}%")
        print(f"  체크일: {result['check_days']}")
