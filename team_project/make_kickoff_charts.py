"""PPT용 차트 3장 생성."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from matplotlib import font_manager

# 한글 폰트
for f in ["AppleGothic", "NanumGothic", "Malgun Gothic"]:
    try:
        font_manager.findfont(f, fallback_to_default=False)
        plt.rcParams["font.family"] = f
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)


# 1. 출석률 비교
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
labels = ["고정 일정\n(매주 월)", "랜덤\n(빈도 공개)", "랜덤\n(비공개) ★"]
values = [6.7, 20.0, 20.0]
colors = ["#dee2e6", "#74c0fc", "#5c7cfa"]
bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=2)
for b, v in zip(bars, values):
    ax.text(b.get_x() + b.get_width()/2, v + 0.7, f"{v}%",
            ha="center", fontsize=18, fontweight="bold", color="#1a3a6e")
ax.set_ylim(0, 26)
ax.set_ylabel("학기 평균 출석률 (%)", fontsize=13)
ax.set_title("출석 정책별 학생 출석률 시뮬레이션 결과",
             fontsize=15, fontweight="bold", color="#1a3a6e", pad=15)
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.text(2, 23, "← 강의계획서 적용\n3배 출석률 증가",
        fontsize=11, color="#fa5252", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig(OUT / "chart_attendance.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()


# 2. 기말 인출 시간 비교
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
labels = ["단일 기말\n(40%)", "격주 분산 퀴즈\n(6회 + 기말)"]
values = [7.4, 2.2]
colors = ["#fa5252", "#51cf66"]
bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=2, width=0.5)
for b, v in zip(bars, values):
    ax.text(b.get_x() + b.get_width()/2, v + 0.25, f"{v}초",
            ha="center", fontsize=20, fontweight="bold", color="#1a3a6e")
ax.set_ylabel("기말 시점 인출 시간 (초)", fontsize=13)
ax.set_ylim(0, 9)
ax.set_title("평가 체계별 학생 기억 인출 속도 (Memory Activation 모델)",
             fontsize=15, fontweight="bold", color="#1a3a6e", pad=15)
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.annotate("", xy=(1, 2.4), xytext=(0, 7.2),
            arrowprops=dict(arrowstyle="->", color="#fa5252", lw=2))
ax.text(0.5, 5.5, "3.4배 빠름", fontsize=14, color="#fa5252", fontweight="bold", ha="center")
ax.text(0.5, -1.3, "공식: $B = \\ln(\\sum t_j^{-d})$, $T_{retrieval} = e^{-B}$  (수업 5-7주차)",
        ha="center", fontsize=11, color="#495057")
plt.tight_layout()
plt.savefig(OUT / "chart_memory.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()


# 3. 팀 구성 완성도 곡선 (N에 따라)
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
N = np.arange(3, 31)

def completeness(n, info):
    base = 7 * (1.5 if info else 1.0)
    return np.minimum(1.0, base / n)

ax.plot(N, completeness(N, info=False), "-", color="#fa5252", linewidth=3,
        label="① 정보 무제공 (이름만)")
ax.plot(N, completeness(N, info=True), "-", color="#74c0fc", linewidth=3,
        label="② 프로필 카드 제공")
ax.axhline(y=1.0, color="#51cf66", linewidth=3, linestyle="--",
           label="③ 매칭 알고리즘 (N과 무관)")

ax.axvspan(8, 30, color="#fff3bf", alpha=0.4)
ax.text(20, 0.35, "WM 한계 초과\nSatisficing 영역",
        ha="center", fontsize=12, color="#e67700", fontweight="bold")
ax.axvline(x=7, linestyle=":", color="#495057", alpha=0.5)
ax.text(7.2, 0.05, "Miller 7±2", fontsize=10, color="#495057")

ax.set_xlabel("팀원 후보 수 N (명)", fontsize=13)
ax.set_ylabel("팀 구성 평가 완성도 (0~1)", fontsize=13)
ax.set_title("팀 구성: 후보 수와 작업 기억 한계의 관계",
             fontsize=15, fontweight="bold", color="#1a3a6e", pad=15)
ax.legend(loc="lower left", fontsize=11, frameon=True)
ax.set_ylim(0, 1.15)
ax.grid(alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(OUT / "chart_team.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()


print(f"✅ 차트 3장 생성: {OUT}")
