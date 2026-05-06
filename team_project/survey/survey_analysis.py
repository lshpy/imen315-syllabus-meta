"""T1 설문 분석 — Vignette 응답으로 4가지 가설 검정.

입력:
    team_project/survey/data/survey_responses.csv
    필요 컬럼: pid, manipulation_check, frame, leader_intent, N_candidates,
              team_satisfaction, attend_condition, absence_intent,
              eval_system, weekly_study_time
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import scipy.stats as stats

DATA = Path(__file__).parent / "data" / "survey_responses.csv"


def load() -> pd.DataFrame:
    if not DATA.exists():
        raise FileNotFoundError(f"설문 응답이 아직 없음: {DATA}\n응답 수집 후 실행")
    df = pd.read_csv(DATA)
    return df[df.manipulation_check == 1].copy()


def h1_framing(df: pd.DataFrame) -> None:
    """H1: gain frame vs loss frame -> 팀장 지원 의도"""
    gain = df.loc[df.frame == "gain", "leader_intent"]
    loss = df.loc[df.frame == "loss", "leader_intent"]
    t, p = stats.ttest_ind(gain, loss, equal_var=False)
    pooled = df.leader_intent.std(ddof=1)
    d = (loss.mean() - gain.mean()) / pooled
    print(f"[H1 Framing]  M_gain={gain.mean():.2f}, M_loss={loss.mean():.2f},"
          f" t={t:.2f}, p={p:.3f}, Cohen's d={d:.2f}")


def h2_satisficing(df: pd.DataFrame) -> None:
    """H2: 후보 수 N=3/7/15 -> 만족도 (1원 ANOVA)"""
    groups = [g.team_satisfaction.values for _, g in df.groupby("N_candidates")]
    f, p = stats.f_oneway(*groups)
    print(f"[H2 Satisficing] F={f:.2f}, p={p:.3f}")
    try:
        import pingouin as pg
        print(pg.pairwise_tukey(data=df, dv="team_satisfaction", between="N_candidates"))
    except ImportError:
        print("(pingouin 미설치 → Tukey 생략)")


def h3_attend(df: pd.DataFrame) -> None:
    """H3: 출석 조건 within-subject -> 결석 의도"""
    try:
        import pingouin as pg
        print(pg.rm_anova(data=df, dv="absence_intent",
                          within="attend_condition", subject="pid"))
    except ImportError:
        print("[H3] pingouin 필요. pip install pingouin")


def h4_memory(df: pd.DataFrame) -> None:
    """H4: 평가 체계별 학습시간 분산 비교"""
    var_a = df.loc[df.eval_system == "single", "weekly_study_time"].var()
    var_b = df.loc[df.eval_system == "biweekly", "weekly_study_time"].var()
    f = var_a / var_b
    print(f"[H4 Memory]  var_single={var_a:.2f}, var_biweekly={var_b:.2f},"
          f" F-ratio={f:.2f}")


if __name__ == "__main__":
    df = load()
    print(f"분석 표본 N={len(df)}\n")
    h1_framing(df)
    h2_satisficing(df)
    h3_attend(df)
    h4_memory(df)
