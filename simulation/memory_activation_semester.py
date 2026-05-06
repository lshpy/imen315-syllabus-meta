"""
시뮬레이션 2: 학기별 Base-level Activation
================================================
수업 공식: B_i = ln(Σ t_j^(-d))
인출 시간: T_retrieval = e^(-B_i)

평가 체계별로 기말고사 시점에서 각 주차 수업 내용의 base-level activation을 비교한다.
- 시나리오 A: 단일 기말고사 (현 강의계획서)
- 시나리오 B: 중간고사 추가 (이전 학기)
- 시나리오 C: 격주 분산 퀴즈 (개선안)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── 파라미터 ─────────────────────────────────
D = 0.5           # 쇠퇴 파라미터 (ACT-R 표준)
N_WEEKS = 15
EXAM_DAY = 105    # 기말고사 시점 (15주차 = 105일)


def base_level_activation(rehearsal_days: list, current_day: float,
                          d: float = D) -> float:
    """수업 공식: B_i = ln(Σ t_j^(-d))"""
    diffs = [current_day - t for t in rehearsal_days if current_day > t]
    if not diffs:
        return -np.inf
    summation = sum(t ** (-d) for t in diffs if t > 0)
    if summation <= 0:
        return -np.inf
    return np.log(summation)


def get_rehearsal_schedule(scenario: str, week: int) -> list:
    """
    각 주차 수업 내용($i$)이 학기 동안 어떤 시점에 학습/인출되는지.
    week: 1~15 (주차)
    반환: 학습/인출 시점들 (일 단위)
    """
    initial_study_day = (week - 1) * 7  # 그 주에 처음 학습

    if scenario == 'single_final':
        # 단일 기말: 그 주에만 학습
        return [initial_study_day]

    elif scenario == 'with_midterm':
        # 중간고사 (8주차) 추가: 1-7주차 내용은 8주차 직전에 1회 더 인출
        if week <= 7:
            midterm_review = 49  # 7주차 말 = 49일 (중간고사 직전)
            return [initial_study_day, midterm_review]
        else:
            return [initial_study_day]

    elif scenario == 'biweekly_quiz':
        # 격주 분산 퀴즈: 2주마다 직전 2주 내용 인출
        # 퀴즈는 2,4,6,8,10,12,14주차 말 = 14, 28, 42, 56, 70, 84, 98일
        quiz_days = [14, 28, 42, 56, 70, 84, 98]
        rehearsals = [initial_study_day]
        for q in quiz_days:
            # 직전 2주 내용 = (q/7)-1 ~ q/7 주차
            quiz_week = q / 7
            if quiz_week - 2 < week <= quiz_week:
                rehearsals.append(q)
        return rehearsals

    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def simulate_semester_activation(scenario: str) -> dict:
    """학기 전체 주차의 기말 시점 activation 계산."""
    activations = []
    retrieval_times = []
    schedules = []

    for week in range(1, N_WEEKS + 1):
        rehearsals = get_rehearsal_schedule(scenario, week)
        B = base_level_activation(rehearsals, EXAM_DAY)
        T = np.exp(-B) if B > -np.inf else np.inf

        activations.append(B)
        retrieval_times.append(T)
        schedules.append(rehearsals)

    return {
        'scenario': scenario,
        'activations': np.array(activations),
        'retrieval_times': np.array(retrieval_times),
        'schedules': schedules,
        'mean_activation': np.mean(activations),
        'mean_retrieval_time': np.mean(retrieval_times)
    }


def plot_activation_curves(save: bool = True):
    """주차별 activation을 시간에 따라 시각화."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    scenarios = {
        '단일 기말 (현 강의계획서)': ('single_final', '#E74C3C'),
        '중간고사 추가':              ('with_midterm', '#F39C12'),
        '격주 분산 퀴즈 (개선안)':   ('biweekly_quiz', '#2ECC71'),
    }

    results = {}

    # 그래프 A: 기말 시점 주차별 activation
    ax = axes[0]
    for label, (key, color) in scenarios.items():
        r = simulate_semester_activation(key)
        results[label] = (r, color)
        ax.plot(range(1, N_WEEKS + 1), r['activations'], marker='o',
                label=label, color=color, linewidth=2, markersize=6)

    ax.set_xlabel('수업 주차', fontsize=11)
    ax.set_ylabel('기말 시점 Base-level Activation $B_i$', fontsize=11)
    ax.set_title('기말고사 시점 주차별 청크 activation\n($B_i = \\ln(\\sum t_j^{-d}),\\, d=0.5$)',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(alpha=0.3)
    ax.set_xticks(range(1, N_WEEKS + 1))

    # 그래프 B: 평균 activation 및 인출 시간 비교 막대
    ax = axes[1]
    labels = list(results.keys())
    means = [r['mean_activation'] for r, _ in results.values()]
    times = [r['mean_retrieval_time'] for r, _ in results.values()]
    colors = [c for _, c in results.values()]

    x = np.arange(len(labels))
    width = 0.35

    bars1 = ax.bar(x - width/2, means, width, label='평균 Activation $B_i$',
                   color=colors, alpha=0.7, edgecolor='black')
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + width/2, times, width, label='평균 인출 시간 $T_{retrieval}$',
                    color=colors, alpha=0.4, hatch='//', edgecolor='black')

    for bar, val in zip(bars1, means):
        ax.text(bar.get_x() + bar.get_width()/2, val - 0.15, f'{val:.2f}',
                ha='center', va='top', fontsize=10, fontweight='bold')
    for bar, val in zip(bars2, times):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.5, f'{val:.1f}s',
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([l.split('(')[0].strip() for l in labels],
                       fontsize=9, rotation=10)
    ax.set_ylabel('평균 Activation $B_i$', fontsize=11)
    ax2.set_ylabel('평균 인출 시간 $T_{retrieval} = e^{-B_i}$ (s)', fontsize=11)
    ax.set_title('평가 체계별 학기 평균 activation과 인출 시간',
                 fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')

    # 범례 통합
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)

    plt.tight_layout()

    if save:
        path = os.path.join(FIGURES_DIR, 'sim2_memory_activation.png')
        plt.savefig(path, dpi=200, bbox_inches='tight')
        print(f"[저장] {path}")

    plt.close()
    return results


if __name__ == '__main__':
    print("=" * 60)
    print("시뮬레이션 2: 학기별 Base-level Activation")
    print("=" * 60)

    results = plot_activation_curves()

    print("\n── 결과 요약 ──")
    for label, (r, _) in results.items():
        print(f"\n{label}:")
        print(f"  평균 activation:  {r['mean_activation']:.3f}")
        print(f"  평균 인출 시간:   {r['mean_retrieval_time']:.2f}초")
        print(f"  3주차 청크 B:    {r['activations'][2]:.3f}")
        print(f"  3주차 인출 시간: {r['retrieval_times'][2]:.2f}초")
