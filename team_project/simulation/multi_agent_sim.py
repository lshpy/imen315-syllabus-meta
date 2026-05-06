"""다중 에이전트 시뮬 — 팀과제 T2 트랙
개인과제의 단일 학생 평균 모델을 N=1000 학생 분포 모델로 확장.

사용:
    python team_project/simulation/multi_agent_sim.py

산출:
    team_project/simulation/figures/multi_agent_distribution.png
    team_project/simulation/figures/intervention_effect.png
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)


@dataclass
class Student:
    alpha: float       # 학습률 (Utility Learning)
    d: float           # 망각 파라미터 (Base-level Activation)
    WM: int            # 작업기억 청크 용량
    motivation: float  # 동기 [0,1]


def sample_population(N: int = 1000) -> list[Student]:
    return [
        Student(
            alpha=float(np.clip(rng.normal(0.15, 0.05), 0.01, None)),
            d=float(np.clip(rng.normal(0.50, 0.10), 0.10, None)),
            WM=int(rng.choice([5, 6, 7, 8, 9], p=[.10, .20, .40, .20, .10])),
            motivation=float(np.clip(rng.normal(0.50, 0.20), 0, 1)),
        )
        for _ in range(N)
    ]


def utility_learning(s: Student, n_weeks: int = 15, checks_per_week: int = 2,
                     reward_random: bool = False) -> float:
    """U(n) = U(n-1) + alpha * (R(n) - U(n-1)). 출석률 반환."""
    U = 0.0
    attended = []
    for _ in range(n_weeks):
        for _c in range(checks_per_week):
            attend_prob = 1 / (1 + np.exp(-5 * (U + s.motivation - 0.5)))
            went = rng.random() < attend_prob
            attended.append(went)
            if went:
                R = 1.0
            elif reward_random and rng.random() < 0.3:
                R = -1.0
            else:
                R = 0.0
            U = U + s.alpha * (R - U)
    return float(np.mean(attended))


def memory_activation(s: Student, study_weeks: list[int], retrieval_week: int = 15) -> float:
    """B_i = ln(sum t_j^-d). retrieval_week 기준."""
    t = np.array([(retrieval_week - sw) * 7 for sw in study_weeks if (retrieval_week - sw) * 7 > 0],
                 dtype=float)
    if len(t) == 0:
        return -np.inf
    return float(np.log(np.sum(t ** (-s.d))))


def team_decision_completeness(s: Student, n_candidates: int, info_provided: bool) -> float:
    base = s.WM * (1.5 if info_provided else 1.0)
    return float(min(1.0, base / n_candidates))


def run() -> pd.DataFrame:
    pop = sample_population(1000)
    rows = []
    for s in pop:
        rows.append({
            "alpha": s.alpha, "d": s.d, "WM": s.WM, "motivation": s.motivation,
            "attend_fixed": utility_learning(s, reward_random=False),
            "attend_random": utility_learning(s, reward_random=True),
            "act_single_final": memory_activation(s, [3]),
            "act_spaced": memory_activation(s, [3, 5, 7, 9, 11, 13]),
            "team_no_info_N15": team_decision_completeness(s, 15, info_provided=False),
            "team_with_info_N7": team_decision_completeness(s, 7, info_provided=True),
        })
    return pd.DataFrame(rows)


def report(df: pd.DataFrame) -> None:
    print("=== 평균 (전체 분포) ===")
    print(df[["attend_fixed", "attend_random", "act_single_final", "act_spaced",
              "team_no_info_N15", "team_with_info_N7"]].mean().round(3))

    print("\n=== 하위 25% (저성취 학생 보호 관점) ===")
    print(df[["attend_fixed", "attend_random", "act_single_final", "act_spaced",
              "team_no_info_N15", "team_with_info_N7"]].quantile(0.25).round(3))


def plot(df: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes[0].hist([df.attend_fixed, df.attend_random], bins=20, label=["고정 일정", "랜덤+빈도비공개"])
    axes[0].set_title("출석률 분포 (N=1000 학생)")
    axes[0].set_xlabel("학기 출석률"); axes[0].legend()

    axes[1].hist([df.act_single_final, df.act_spaced], bins=20, label=["단일 기말", "격주 분산 학습"])
    axes[1].set_title("기말 시점 Memory Activation B_i")
    axes[1].set_xlabel("B_i (log scale)"); axes[1].legend()

    axes[2].hist([df.team_no_info_N15, df.team_with_info_N7], bins=20,
                 label=["정보무제공 N=15", "프로필카드 N=7"])
    axes[2].set_title("팀 구성 평가 완성도")
    axes[2].set_xlabel("완성도"); axes[2].legend()

    plt.tight_layout()
    out = OUT / "multi_agent_distribution.png"
    plt.savefig(out, dpi=150)
    print(f"\n저장: {out}")


if __name__ == "__main__":
    df = run()
    report(df)
    plot(df)
    csv_out = OUT.parent / "multi_agent_results.csv"
    df.to_csv(csv_out, index=False)
    print(f"저장: {csv_out}")
