# 팀과제 (Team Project) — IMEN315

> 개인과제([../README.md](../README.md))의 단일 학생 모델을 **다중 에이전트·실증 데이터**로 확장.
> 노션 작업실: [팀 노션 작업실](https://www.notion.so/35877a1e7f6780beb7eecc26948eae0a)

## 디렉터리

```
team_project/
├── simulation/               # T2 다중 에이전트 시뮬
│   ├── multi_agent_sim.py
│   └── figures/
├── survey/                   # T1 설문 분석
│   ├── survey_analysis.py
│   └── data/                 # CSV는 .gitignore (개인정보)
└── behavior_exp/             # T3 행동 미니 실험
    └── (TBD)
```

## 빠른 실행

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy pandas scipy pingouin matplotlib
python team_project/simulation/multi_agent_sim.py
```

## 가설 (T1 설문)

| 가설 | 이론 | 핵심 |
|---|---|---|
| H1 | Framing / Prospect | gain vs loss frame → 참여 의도 차이 |
| H2 | Satisficing | 후보 수 N=8 이상에서 완성도 급감 |
| H3 | Utility Learning | 가변비율+비공개 조건 결석 의도 최저 |
| H4 | Forgetting Curve | 분산 평가 → 학습시간 분산도 ↑ |
