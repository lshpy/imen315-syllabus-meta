"""시뮬레이션 예시 추가 차트 생성"""
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

matplotlib.rcParams["font.family"] = ["AppleGothic", "Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)


# ── 1. 분포 효과 (평균 vs 하위 25%)
fig, ax = plt.subplots(figsize=(9, 5))
groups = ["기존 강의계획서", "분산 평가 도입"]
average = [12.5, 10.2]
bottom_25 = [22.3, 13.5]
x = np.arange(len(groups))
w = 0.35
b1 = ax.bar(x - w/2, average, w, label="평균 학생", color="#4F46E5")
b2 = ax.bar(x + w/2, bottom_25, x*0+w, label="하위 25% 학생 (저성취)", color="#EC4899")
ax.set_ylabel("학기말 인출 시간 (초)", fontsize=12)
ax.set_title("개선안의 진짜 효과는 \"약한 학생\"에게서 보인다", fontsize=14, weight="bold")
ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=12)
ax.legend(fontsize=11, loc="upper right")
ax.grid(axis="y", alpha=0.3)
for bars in [b1, b2]:
    for bar in bars:
        ax.annotate(f"{bar.get_height():.1f}s",
                    xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, weight="bold")
ax.set_ylim(0, 28)
plt.tight_layout()
plt.savefig(OUT / "chart_distribution.png", dpi=150)
plt.close()
print("✅ chart_distribution.png")


# ── 2. Memory activation 시간 경과 곡선
fig, ax = plt.subplots(figsize=(9, 5))
days = np.arange(1, 110)
d = 0.5
# 단일 기말: 3주차에만 학습
B_single = np.log(np.where(days >= 21, (days - 21) ** -d, np.inf))
B_single = np.where(np.isfinite(B_single), B_single, np.nan)
# 격주 퀴즈: 3, 5, 7, 9, 11, 13주차 학습
qweeks = [21, 35, 49, 63, 77, 91]
def b_spaced(t):
    contributions = []
    for w in qweeks:
        if t > w:
            contributions.append((t - w) ** -d)
    return np.log(sum(contributions)) if contributions else np.nan
B_spaced = np.array([b_spaced(t) for t in days])

ax.plot(days, B_single, color="#F59E0B", linewidth=3, label="단일 기말 (한 번만 학습)")
ax.plot(days, B_spaced, color="#10B981", linewidth=3, label="격주 퀴즈 (분산 학습)")
ax.axvline(x=105, linestyle="--", color="#EC4899", linewidth=2)
ax.text(105.5, -2.5, "기말고사일\n(15주차)", color="#EC4899", fontsize=10, weight="bold")
ax.set_xlabel("학기 경과일 (days)", fontsize=12)
ax.set_ylabel("기억 활성도 B (높을수록 잘 떠오름)", fontsize=12)
ax.set_title("시간이 지나면서 기억이 어떻게 사라지는가", fontsize=14, weight="bold")
ax.legend(fontsize=11, loc="upper right")
ax.grid(alpha=0.3)
ax.set_ylim(-3, 0.5)
plt.tight_layout()
plt.savefig(OUT / "chart_memory_curve.png", dpi=150)
plt.close()
print("✅ chart_memory_curve.png")


# ── 3. 친분 네트워크 시각화
import networkx as nx
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
rng = np.random.default_rng(42)

G = nx.watts_strogatz_graph(20, k=4, p=0.3, seed=42)
pos = nx.spring_layout(G, seed=7)
leader = 0

conditions = [
    ("친한 사람만 (현실)", "#EC4899",
     sorted(G.neighbors(leader), key=lambda x: x)[:5]),
    ("머리에 떠오르는 사람 (WM 한계)", "#F59E0B",
     [n for n in list(G.neighbors(leader))[:5]]),
    ("프로필 카드 보고 (이상)", "#10B981",
     sorted(G.nodes(), key=lambda x: rng.random())[:5]),
]

for ax, (title, color, picked) in zip(axes, conditions):
    node_colors = []
    sizes = []
    for n in G.nodes():
        if n == leader:
            node_colors.append("#FCD34D"); sizes.append(700)
        elif n in picked:
            node_colors.append(color); sizes.append(500)
        else:
            node_colors.append("#E5E7EB"); sizes.append(250)
    nx.draw(G, pos, ax=ax, node_color=node_colors, node_size=sizes,
            with_labels=False, edge_color="#D1D5DB", width=1)
    ax.set_title(title, fontsize=12, weight="bold")

fig.suptitle("팀장 선택 방식별 그래프 — 노란색=팀장, 컬러=선택된 5명",
             fontsize=14, weight="bold", y=1.02)
plt.tight_layout()
plt.savefig(OUT / "chart_network.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ chart_network.png")

print(f"\n저장: {OUT}")
