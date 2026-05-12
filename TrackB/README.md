# IMEN315 교실 자리 외우기 게임

인간공학 텀프로젝트 — **Track A: 가설 2 (Testing Effect) 검증**

## 실험 설계

연예인 6명이 5×5 교실에 앉은 자리를 외우는 게임. 두 가지 학습 방식의 효과를 비교.

| 조건 A — 한 번에 학습 | 조건 B — 학습 + 중간 퀴즈 |
|---|---|
| 18초 학습 → 최종 시험 6문제 | (6초 학습 → 2문제) × 3사이클 → 최종 시험 6문제 |

- **학습 시간 동일** (18초)
- **최종 시험 문항 수 동일** (6문제)
- 차이는 **중간 인출 연습 유무**

## 통제 변수

- **카운터밸런싱**: 참여자의 50%는 A→B, 50%는 B→A 순서로 진행 (순서 효과 통제)
- **무작위 배치**: 참여자마다 연예인의 자리 배치를 새로 셔플
- **시험 문항 순서 셔플**: 학습한 순서와 시험 순서 분리

## 측정 변수

- **정답률** (단일 학습 vs 인출 연습)
- **응답시간 (ms)**: First Click + Page Submit 두 지점
- **사후 자기보고**: 난이도, 집중도

## 이론적 배경

- Roediger & Karpicke (2006) "Test-Enhanced Learning"
- Testing Effect / Retrieval Practice paradigm
- 형성평가(formative assessment) vs 단일 총괄평가(summative)

## 파일 구조

```
TrackB/
├── index.html         # 메인 실험 페이지
├── experiment.html    # 동일 파일 (호환용)
├── photos/            # 연예인 사진
│   ├── karina.jpg
│   ├── jangwonyoung.png
│   ├── byeonwooseok.webp
│   ├── choosunghoon.webp
│   ├── limyoungwoong.jpg
│   └── sullyoon.webp
└── SETUP_GUIDE.md     # Google Sheets 자동 수집 설정
```

## 배포

[Netlify](https://imen315-seat-game.netlify.app) — 폴더 통째로 드래그&드롭

## 데이터 수집

Google Apps Script → Google Sheets 자동 누적 (실시간)
