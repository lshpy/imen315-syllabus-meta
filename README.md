# IMEN315 Syllabus Meta-Analysis

**IMEN315 인간공학 강의계획서의 인지·행동 유도 메커니즘에 대한 인간공학적 역(逆)분석**

> IMEN315 인간공학 | 2026-1학기 | 고려대학교 산업경영공학부
> 개인과제 (1단계)

---

## 개요

본 개인과제는 **메타적(meta) 접근**을 택한다. 즉, 본 수업(IMEN315 인간공학)의 강의계획서와 텀프로젝트 안내서에 명시된 설계 요소들을, 바로 이 수업에서 배운 인간공학 이론으로 역분석한다.

> "이 수업의 평가 체계가 학생의 인지적·행동적 패턴에 어떤 영향을 유발하는가"

---

## 분석 대상 (강의계획서의 4개 설계 요소)

| 설계 요소 | 내용 |
|---------|------|
| (1) 랜덤 출석 확인 | "출석 예정일 외에도 임의로 출석 확인" (참여도 10%) |
| (2) 중간고사 폐지, 단일 기말고사 | 중간고사 미시행(8주차 휴강), 기말고사 40% |
| (3) 팀 구성 규칙 | 팀장 최대 2명 팀원 선발, 미응답 시 자동 배정 |
| (4) 차등 인센티브 | 팀장 +10점 가산, 기여도 저조 시 감점 |

---

## 적용한 수업 이론

| 설계 요소 | 적용 이론 (수업 주차) | 핵심 공식 |
|---------|-------------------|---------|
| (1) 랜덤 출석 | Utility Learning (6주차), Vigilance (3주차) | `U_i(n) = U_i(n-1) + α[R_i(n) - U_i(n-1)]` |
| (2) 단일 기말 | Forgetting Curve (7주차), Base-level Activation | `B_i = ln(Σ t_j^(-d))`, `R(t) = k·t^(-d)` |
| (3) 팀 구성 | Decision Making (12주차), Working Memory | 7±2 chunk, Satisficing |
| (4) 인센티브 | Framing Effect, Prospect Theory | gain vs loss frame |

---

## 프로젝트 구조

```
syllabus_meta_project/
├── README.md                          # 이 파일
├── report/
│   ├── individual_assignment.tex      # LaTeX 소스
│   └── individual_assignment.pdf      # 제출용 PDF (6페이지)
└── figures/                           # 참고 그림 (TikZ로 문서 내 생성)
```

---

## 핵심 통찰

1. **랜덤 출석**은 Skinner의 가변 비율 강화 스케줄과 구조적으로 동일 → 출석 행동을 절차 기억으로 고착시키는 효과
2. **단일 기말고사**는 수업에서 가르치는 Consolidation·Spaced Practice 원리와 역설적으로 상충
3. **팀 구성 규칙**은 Working Memory 한계로 인해 satisficing(그럭저럭 만족)으로 수렴
4. **차등 인센티브**는 gain/loss frame 비대칭으로 인해 Social Loafing을 암묵적으로 유인

---

## 설계 개선 제안

각 설계 요소별 개선안을 인간공학 이론 기반으로 제안:

- **랜덤 출석**: 출석 확인 빈도 하한 공지 + 1분 리콜 퀴즈 병행
- **단일 기말**: 격주 저부담 퀴즈 6회로 분산 + 누적 복습 문항 포함
- **팀 구성**: 구조화된 프로필 카드 + 72시간 조정 기간
- **인센티브**: 기여도 rubric 명시 + 팀장 가산점을 기여도 연동 지급

---

## 컴파일 방법

```bash
cd report
xelatex individual_assignment.tex
xelatex individual_assignment.tex   # 2차 컴파일로 링크 확정
```

XeLaTeX + Noto Sans KR 폰트 필요.

---

## 참고문헌 (보고서에 수록)

- Lee, J. D., Wickens, C. D., Liu, Y., & Boyle, L. N. (2017). *Designing for people*. (본 수업 교재)
- Anderson, J. R., & Lebiere, C. (1998). *The atomic components of thought*.
- Baddeley, A. D. (1986). *Working memory*.
- Kahneman, D. (2011). *Thinking, fast and slow*.
- Karpicke, J. D., & Roediger, H. L. (2008). The critical importance of retrieval for learning. *Science*.
- Rasmussen, J. (1983). Skills, rules, and knowledge. *IEEE SMC*.
- Tversky, A., & Kahneman, D. (1981). The framing of decisions. *Science*.
- Ebbinghaus, H. (1885). *Über das Gedächtnis*.
- Skinner, B. F. (1953). *Science and human behavior*.

---

## License

IMEN315 Human Factors Engineering (Korea University, 2026 Spring) 개인과제.
