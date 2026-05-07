"""사회 네트워크 기반 팀 구성 시뮬레이션 (T3)
WM 한계와 친분 휴리스틱이 팀 구성에 미치는 영향을 그래프 위에서 시뮬레이션.

사용:
    pip install networkx numpy matplotlib
    python team_project/network_sim/social_network_team.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

INTERESTS = ["AI", "HCI", "Stats", "Design"]
N_STUDENTS = 30
TEAM_SIZE = 5
WM_LIMIT = 7  # Miller 7±2
LEADER_ID = 0


def build_population(n: int = N_STUDENTS) -> nx.Graph:
    """30명짜리 small-world 친분 네트워크 + 노드 속성"""
    G = nx.watts_strogatz_graph(n, k=6, p=0.3, seed=42)
    for node in G.nodes():
        G.nodes[node]["ability"] = float(np.clip(rng.normal(7, 1.5), 1, 10))
        G.nodes[node]["interest"] = rng.choice(INTERESTS)
        G.nodes[node]["availability"] = int(rng.integers(1, 6))
    # 친분 가중치(거리 기반)
    for u, v in G.edges():
        G[u][v]["closeness"] = float(rng.uniform(0.3, 1.0))
    return G


def friendship_score(G: nx.Graph, leader: int, candidate: int) -> float:
    if not G.has_edge(leader, candidate):
        return 0.0
    return G[leader][candidate]["closeness"]


def select_random(G: nx.Graph, leader: int, k: int) -> list[int]:
    candidates = [n for n in G.nodes() if n != leader]
    return list(rng.choice(candidates, size=k, replace=False))


def select_friendship(G: nx.Graph, leader: int, k: int) -> list[int]:
    candidates = [n for n in G.nodes() if n != leader]
    scored = sorted(candidates, key=lambda n: friendship_score(G, leader, n), reverse=True)
    return scored[:k]


def select_ability(G: nx.Graph, leader: int, k: int) -> list[int]:
    candidates = [n for n in G.nodes() if n != leader]
    scored = sorted(candidates, key=lambda n: G.nodes[n]["ability"], reverse=True)
    return scored[:k]


def select_wm_satisficing(G: nx.Graph, leader: int, k: int, wm: int = WM_LIMIT) -> list[int]:
    """WM 한계: 친분 높은 순 wm명만 떠올린 후, 그 안에서 친분 우선 k명."""
    neighbors = sorted(
        [n for n in G.nodes() if n != leader],
        key=lambda n: friendship_score(G, leader, n),
        reverse=True,
    )
    pool = neighbors[:wm]
    pool_sorted = sorted(pool, key=lambda n: friendship_score(G, leader, n), reverse=True)
    return pool_sorted[:k]


def select_profile_card(G: nx.Graph, leader: int, k: int) -> list[int]:
    """프로필 카드 → 모든 후보 정보 균형 선택 (역량 + 관심 다양성)."""
    candidates = [n for n in G.nodes() if n != leader]
    chosen: list[int] = []
    used_interests: set[str] = set()
    for n in sorted(candidates, key=lambda x: G.nodes[x]["ability"], reverse=True):
        interest = G.nodes[n]["interest"]
        if interest not in used_interests or len(chosen) >= len(INTERESTS):
            chosen.append(n)
            used_interests.add(interest)
        if len(chosen) == k:
            break
    return chosen


def metrics(G: nx.Graph, team: list[int], leader: int) -> dict[str, float]:
    abilities = [G.nodes[n]["ability"] for n in team]
    interests = [G.nodes[n]["interest"] for n in team]
    friend_count = sum(1 for n in team if G.has_edge(leader, n))
    counts = np.array([interests.count(i) for i in INTERESTS], dtype=float)
    p = counts / counts.sum() if counts.sum() else counts
    entropy = float(-np.sum([pi * np.log2(pi) for pi in p if pi > 0]))
    return {
        "friend_bias": friend_count / len(team),
        "ability_mean": float(np.mean(abilities)),
        "ability_std": float(np.std(abilities)),
        "interest_entropy": entropy,
    }


def run_all() -> dict[str, dict]:
    G = build_population()
    conditions = {
        "A. 무작위": select_random,
        "B. 친분 우선": select_friendship,
        "C. 역량 우선": select_ability,
        "D. WM 한계 (현실)": select_wm_satisficing,
        "E. 프로필카드": select_profile_card,
    }
    results = {}
    for name, fn in conditions.items():
        team = fn(G, LEADER_ID, TEAM_SIZE)
        results[name] = {"team": team, **metrics(G, team, LEADER_ID)}
    return G, results


def visualize(G: nx.Graph, results: dict) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    pos = nx.spring_layout(G, seed=42)
    palette = {True: "#ff6b6b", False: "#4dabf7"}

    for ax, (name, res) in zip(axes.flatten(), results.items()):
        team = set(res["team"])
        node_colors = [
            "#ffd43b" if n == LEADER_ID
            else "#ff6b6b" if n in team
            else "#dee2e6"
            for n in G.nodes()
        ]
        node_sizes = [600 if n == LEADER_ID or n in team else 300 for n in G.nodes()]
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
        ax.set_title(
            f"{name}\n친분 편향 {res['friend_bias']:.2f} · 역량 std {res['ability_std']:.2f} · "
            f"관심 entropy {res['interest_entropy']:.2f}"
        )
        ax.axis("off")

    axes.flatten()[5].axis("off")
    axes.flatten()[5].text(
        0.05, 0.5,
        "노란색 = 팀장 (Node 0)\n빨간색 = 선택된 팀원 5명\n회색 = 비선택 후보\n\n"
        "지표 해설:\n"
        "• 친분 편향: 팀장과 직접 연결 비율 (0~1)\n"
        "• 역량 std: 팀 역량 표준편차 (낮을수록 균형)\n"
        "• 관심 entropy: 다양성 (높을수록 균형)",
        fontsize=10, va="center"
    )

    plt.tight_layout()
    out = OUT / "team_formation_networks.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"저장: {out}")


def report(results: dict) -> None:
    print("\n=== 조건별 팀 구성 결과 ===")
    print(f"{'조건':<25} {'친분편향':>8} {'역량평균':>8} {'역량std':>8} {'다양성':>8}")
    for name, res in results.items():
        print(f"{name:<25} {res['friend_bias']:>8.2f} {res['ability_mean']:>8.2f} "
              f"{res['ability_std']:>8.2f} {res['interest_entropy']:>8.2f}")


if __name__ == "__main__":
    G, results = run_all()
    report(results)
    visualize(G, results)
