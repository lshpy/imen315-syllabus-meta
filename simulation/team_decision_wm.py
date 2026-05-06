"""
시뮬레이션 3: 팀 구성 의사결정과 Working Memory 한계
========================================================
수업 공식 응용:
- T = T_perception + T_encoding + T_retrieval + T_decide + T_action
- WM 용량 = 7±2 청크
- 후보 N명 × 정보 차원 4 (역량·친분·스케줄·신뢰도) = 4N 청크

세 시나리오에서 후보 수 증가에 따른 결정 시간과 평가 완성도를 시뮬레이션한다.
- 시나리오 A: 정보 무제공 (현 텀프로젝트 안내서)
- 시나리오 B: 프로필 카드 제공 (구조화 정보)
- 시나리오 C: 선호 매칭 알고리즘 (의사결정 지원)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

FIGURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── 파라미터 ─────────────────────────────────
WM_CAPACITY = 7              # 작업 기억 용량 (Miller 7±2)
INFO_DIMS = 4                # 후보당 평가 차원 (역량·친분·스케줄·신뢰도)
T_PER_CANDIDATE_RAW = 1.5    # 정보 무제공 시 후보 1명 평가 시간 (분)
T_PER_CANDIDATE_CARD = 0.6   # 프로필 카드 시
T_PER_CANDIDATE_ALGO = 0.05  # 알고리즘 보조 시


def evaluate_scenario(scenario: str, n_candidates: int) -> dict:
    """
    후보 수 N에서의 평가 완성도, 결정 시간, 결정 품질을 계산.
    """
    if scenario == 'no_info':
        # WM에 4N 청크 필요 → 7개 초과 시 일부 후보 평가 누락
        n_evaluable = min(n_candidates, WM_CAPACITY // INFO_DIMS * n_candidates // n_candidates if n_candidates > 0 else 0)
        # 실제 평가 가능 인원: 청크 한계로 추정
        max_full = WM_CAPACITY / INFO_DIMS  # 약 1.75명만 4차원 비교 가능
        # 부분 평가까지 포함 → satisficing
        n_evaluable_partial = min(n_candidates,
                                  int(WM_CAPACITY / max(1, INFO_DIMS - 1)) + 2)
        completion = min(1.0, n_evaluable_partial / n_candidates)
        decision_time = T_PER_CANDIDATE_RAW * n_evaluable_partial + 5
        # 품질: 평가 못 한 후보 중 최적이 있을 확률 → 누락분 비례 감소
        quality = 0.4 + 0.5 * completion  # 0.4~0.9 범위
        # satisficing 표시
        is_satisficing = completion < 0.7

    elif scenario == 'profile_card':
        # 청킹 지원: 4차원을 1청크로 묶어 평가 → WM에 7명까지 유지 가능
        chunked_capacity = WM_CAPACITY  # 1청크/후보
        completion = min(1.0, chunked_capacity / max(n_candidates, 1)) if n_candidates > chunked_capacity else 0.85
        # 7명 이내면 완전 평가, 초과 시 비례 감소하지만 raw보다 효율
        if n_candidates <= chunked_capacity:
            completion = 0.92
            decision_time = T_PER_CANDIDATE_CARD * n_candidates + 3
        else:
            completion = 0.92 * (chunked_capacity / n_candidates) + 0.05
            decision_time = T_PER_CANDIDATE_CARD * n_candidates + 5
        quality = 0.6 + 0.3 * completion
        is_satisficing = completion < 0.8

    elif scenario == 'matching_algo':
        # 알고리즘이 모든 후보를 평가 → WM 부담 거의 없음
        completion = 1.0
        decision_time = T_PER_CANDIDATE_ALGO * n_candidates + 2
        quality = 0.92
        is_satisficing = False

    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    return {
        'n_candidates': n_candidates,
        'completion': completion,
        'decision_time': decision_time,
        'quality': quality,
        'is_satisficing': is_satisficing,
        'scenario': scenario
    }


def plot_team_decision(save: bool = True):
    """후보 수에 따른 결정 시간 vs 품질 그래프."""
    n_range = np.arange(3, 31)

    scenarios = {
        '정보 무제공 (현 안내서)':    ('no_info', '#E74C3C'),
        '프로필 카드 제공':           ('profile_card', '#F39C12'),
        '선호 매칭 알고리즘 (개선안)': ('matching_algo', '#2ECC71'),
    }

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    completion_data = {}
    time_data = {}
    quality_data = {}

    for label, (key, color) in scenarios.items():
        completions, times, qualities = [], [], []
        for n in n_range:
            r = evaluate_scenario(key, n)
            completions.append(r['completion'] * 100)
            times.append(r['decision_time'])
            qualities.append(r['quality'] * 100)
        completion_data[label] = (completions, color)
        time_data[label] = (times, color)
        quality_data[label] = (qualities, color)

    # 그래프 1: 평가 완성도
    ax = axes[0]
    for label, (data, color) in completion_data.items():
        ax.plot(n_range, data, marker='o', label=label, color=color,
                linewidth=2, markersize=4)
    ax.axhline(y=70, color='gray', linestyle='--', alpha=0.5,
               label='satisficing 임계 (70%)')
    ax.set_xlabel('후보 팀원 수 $N$', fontsize=11)
    ax.set_ylabel('평가 완성도 (%)', fontsize=11)
    ax.set_title('후보 수 vs 평가 완성도\n(WM 한계로 satisficing 발생)',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='lower left', fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 110)

    # 그래프 2: 결정 시간
    ax = axes[1]
    for label, (data, color) in time_data.items():
        ax.plot(n_range, data, marker='s', label=label, color=color,
                linewidth=2, markersize=4)
    ax.set_xlabel('후보 팀원 수 $N$', fontsize=11)
    ax.set_ylabel('결정 시간 (분)', fontsize=11)
    ax.set_title('후보 수 vs 결정 시간', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(alpha=0.3)

    # 그래프 3: 결정 품질
    ax = axes[2]
    for label, (data, color) in quality_data.items():
        ax.plot(n_range, data, marker='^', label=label, color=color,
                linewidth=2, markersize=4)
    ax.set_xlabel('후보 팀원 수 $N$', fontsize=11)
    ax.set_ylabel('결정 품질 (역량 매칭 점수, %)', fontsize=11)
    ax.set_title('후보 수 vs 결정 품질', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_ylim(30, 100)

    plt.suptitle('팀 구성 의사결정: WM 한계 ($7\\pm 2$)와 정보 구조화 효과',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save:
        path = os.path.join(FIGURES_DIR, 'sim3_team_decision.png')
        plt.savefig(path, dpi=200, bbox_inches='tight')
        print(f"[저장] {path}")

    plt.close()


if __name__ == '__main__':
    print("=" * 60)
    print("시뮬레이션 3: 팀 구성 의사결정")
    print("=" * 60)

    plot_team_decision()

    print("\n── 후보 10명일 때 결과 ──")
    for scenario in ['no_info', 'profile_card', 'matching_algo']:
        r = evaluate_scenario(scenario, 10)
        print(f"\n{scenario}:")
        print(f"  평가 완성도: {r['completion']*100:.1f}%")
        print(f"  결정 시간:   {r['decision_time']:.1f}분")
        print(f"  결정 품질:   {r['quality']*100:.1f}점")
        print(f"  Satisficing 발생: {r['is_satisficing']}")
