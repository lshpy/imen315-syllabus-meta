# T3 사회 네트워크 시뮬레이션

학생 30명을 그래프 노드로, 친분을 엣지로 표현하고 팀장이 5명을 뽑는 과정을 5가지 조건으로 시뮬레이션.

## 5조건

| 조건 | 알고리즘 | 예측 결과 |
|---|---|---|
| A. 무작위 | random 5명 | 친분 편향 0 |
| B. 친분 우선 | closeness 상위 5명 | 친분 ↑ 역량 ↓ |
| C. 역량 우선 | ability 상위 5명 | 역량 ↑ 친분 0 |
| D. WM 한계 | 친분 상위 7명만 떠올림 → 5명 | satisficing 발현 |
| E. 프로필카드 | 전체 정보 + 관심 다양성 | 균형 |

## 측정

- 친분 편향: 팀장과 직접 연결 비율
- 역량 std: 팀 역량 표준편차
- 관심 entropy: Shannon entropy

## 실행

```bash
pip install networkx numpy matplotlib
python team_project/network_sim/social_network_team.py
```

산출: `figures/team_formation_networks.png`
