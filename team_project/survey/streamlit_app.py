"""IMEN315 강의계획서 인식 조사 — 학습 MBTI 게임
4가지 차원으로 16개 학습 유형 분석.

실행:
    streamlit run team_project/survey/streamlit_app.py
"""
from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="학습 MBTI · IMEN315",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path(__file__).parent / "data" / "streamlit_responses.csv"
DATA_FILE.parent.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────
# 학습 MBTI 정의
# ─────────────────────────────────────────────────
# 4 차원, 각 2 글자 = 16 유형
#
# 1. 동기 축 — 손실회피(L) vs 이득추구(G) [Framing/Prospect]
# 2. 환경 축 — 예측가능(P) vs 무작위적응(R) [Utility Learning]
# 3. 학습 축 — 분산형(D) vs 집중형(C) [Forgetting Curve]
# 4. 결정 축 — 직관(I) vs 분석(A) [Working Memory + Satisficing]
DIMENSIONS = [
    ("동기", "L", "G", "손실 회피", "이득 추구"),
    ("환경", "P", "R", "예측 가능 선호", "무작위 적응"),
    ("학습", "D", "C", "분산 학습", "집중 학습"),
    ("결정", "I", "A", "직관 결정", "분석 결정"),
]

TYPE_PROFILES = {
    "LPDA": {"emoji": "🛡️", "name": "안정의 분석가",
             "desc": "위험을 피하고, 예측 가능한 환경에서, 꾸준히 분산 학습하며, 정보를 체계적으로 분석. 가장 모범적인 유형이지만 변화에 약할 수 있음."},
    "LPDI": {"emoji": "📚", "name": "성실한 직관가",
             "desc": "안정 환경에서 분산 학습은 잘하지만 결정은 빠르게. 친분·직관 기반. 균형 잡힌 학생."},
    "LPCA": {"emoji": "🎯", "name": "기말 집중 전략가",
             "desc": "안정 추구 + 학기말 집중형 + 분석형. 평소엔 살살 하다가 시험 직전 모든 정보 수집해 폭발. 위험."},
    "LPCI": {"emoji": "🦔", "name": "안전한 벼락치기형",
             "desc": "고정 환경 좋아하지만 분산 학습은 못 함. 벼락치기 + 직관 의존. 흔한 한국 대학생 표준."},
    "LRDA": {"emoji": "🦉", "name": "신중한 적응 학자",
             "desc": "변화에 적응 잘하면서 손실은 피하고 분산 학습. 분석가. 매우 견고한 학습자."},
    "LRDI": {"emoji": "🐺", "name": "본능적 생존가",
             "desc": "무작위 환경에서도 분산 학습으로 살아남음. 직관 의존. 위기 대응력 최강."},
    "LRCA": {"emoji": "🎮", "name": "벼락치기 분석가",
             "desc": "변동성에 적응 + 학기말 집중 + 분석. 단기 폭발력 최고. 평소엔 게이밍."},
    "LRCI": {"emoji": "🐌", "name": "도전 회피형 벼락치기",
             "desc": "변화는 받아들이지만 분산 학습 못 하고 직관에 의존. 가장 운에 의존."},

    "GPDA": {"emoji": "🚀", "name": "동기부여형 모범생",
             "desc": "이득 추구 + 안정 + 분산 + 분석. 가산점에 강하게 반응하며 체계적 학습. 이상적 유형."},
    "GPDI": {"emoji": "⚡", "name": "직진 학습자",
             "desc": "이득 보고 달려가며 안정 환경 + 분산 학습. 직관 결정. 빠르고 효율적."},
    "GPCA": {"emoji": "🦅", "name": "기말 폭격기",
             "desc": "이득 추구 + 안정 + 학기말 집중 + 분석. 평소 자기 일 + 시험 직전 폭발. 효율 추구."},
    "GPCI": {"emoji": "🐯", "name": "타고난 벼락치기 천재",
             "desc": "이득 보고 단번에 + 직관 + 집중. 평균 이상 성과 거두지만 운 변수 큼."},
    "GRDA": {"emoji": "🐉", "name": "전천후 도전가",
             "desc": "이득 추구 + 변동성 OK + 분산 + 분석. 어떤 환경에서도 적응. 리더형."},
    "GRDI": {"emoji": "🔥", "name": "직진 모험가",
             "desc": "이득 보고 변화 즐기며 분산 학습. 직관. 활동량 최고."},
    "GRCA": {"emoji": "🎲", "name": "도박형 천재",
             "desc": "이득 + 변동성 + 학기말 집중 + 분석. 위험 감수 + 폭발력. 결과 양극화."},
    "GRCI": {"emoji": "🌪️", "name": "감각적 직관파",
             "desc": "이득 추구 + 변동성 + 집중 + 직관. 감으로 살지만 묘하게 잘됨."},
}


def save_response(record: dict) -> None:
    df_new = pd.DataFrame([record])
    if DATA_FILE.exists():
        df_old = pd.read_csv(DATA_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(DATA_FILE, index=False)


# ─────────────────────────────────────────────────
# 상태 초기화
# ─────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.frame = random.choice(["gain", "loss"])
    st.session_state.n_cand = random.choice([3, 7, 15])
    st.session_state.info_provided = random.choice([True, False])
    # 4 차원 점수
    st.session_state.scores = {"L": 0, "G": 0, "P": 0, "R": 0, "D": 0, "C": 0, "I": 0, "A": 0}


def add_score(letter: str, weight: int = 1):
    st.session_state.scores[letter] += weight


def next_step():
    st.session_state.step += 1
    st.rerun()


# 진행률
TOTAL = 7
if 0 < st.session_state.step < TOTAL:
    st.progress(st.session_state.step / (TOTAL - 1))
    st.caption(f"📖 챕터 {st.session_state.step} / {TOTAL - 1}")


# ─────────────────────────────────────────────────
# 챕터 0: 인트로
# ─────────────────────────────────────────────────
def page_intro():
    st.title("🧬 학습 MBTI")
    st.caption("IMEN315 인간공학 강의계획서 인식 조사")
    st.markdown(
        """
        ### 당신은 어떤 학습자인가요?

        16가지 학습 유형 중 **당신의 유형**을 인간공학 이론으로 분석합니다.

        **4가지 차원**:
        - 🛡️ 손실회피 (L) vs 🚀 이득추구 (G)
        - 📐 예측가능 선호 (P) vs 🎲 무작위 적응 (R)
        - 📚 분산학습 (D) vs 🔥 집중학습 (C)
        - 💭 직관결정 (I) vs 🔍 분석결정 (A)

        ⏱️ 약 5분 · 🎁 완료자 추첨 스타벅스 5장 · 🔒 익명
        """
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.session_state.answers["nickname"] = st.text_input(
            "🧑 익명 닉네임", value="익명의 수강생", max_chars=20
        )
    with col2:
        st.session_state.answers["grade"] = st.selectbox(
            "학년", ["1학년", "2학년", "3학년", "4학년", "기타"]
        )

    if st.button("🧬 시작하기 →", type="primary", use_container_width=True):
        next_step()


# ─────────────────────────────────────────────────
# 챕터 1: 출석 (P vs R 측정)
# ─────────────────────────────────────────────────
def page_attendance():
    st.title("📅 챕터 1 — 출석 정책")
    st.info("**상황**: 비 오는 화요일 아침. 같은 비 오는 날인데 수업 출석 정책이 3가지로 다릅니다.")

    st.markdown("### 🌧️ A — *매주 월요일에만 체크 (예측 가능)*")
    a = st.select_slider(
        "이 정책에서 비 오는 화요일에 갈 의향?",
        ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"],
        value="🤔 모름", key="att_a")

    st.markdown("### 🎲 B — *30회 중 7회 무작위 (횟수만 알려줌)*")
    b = st.select_slider(
        "갈 의향?",
        ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"],
        value="🤔 모름", key="att_b")

    st.markdown("### 🌫️ C — *완전 무작위 (횟수도 비공개)*")
    c = st.select_slider(
        "갈 의향?",
        ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"],
        value="🤔 모름", key="att_c")

    st.markdown("---")
    check = st.radio(
        "🔍 **이해 확인** — 위 셋 중 가장 예측 불가능한 정책은?",
        ["A", "B", "C"], index=2, horizontal=True)

    if st.button("다음 →", type="primary", use_container_width=True):
        m = {"😴 절대 안 감": 1, "😪 별로": 2, "🤔 모름": 3, "🙂 갈까": 4, "🏃 갈래": 5}
        st.session_state.answers.update(
            attend_A=m[a], attend_B=m[b], attend_C=m[c], attend_check=check)

        # P vs R 측정: A에서 잘 가면 P, C에서 잘 가면 R
        if m[a] >= m[c]:
            add_score("P", 2)
        else:
            add_score("R", 2)
        next_step()


# ─────────────────────────────────────────────────
# 챕터 2: 팀장 인센티브 (L vs G)
# ─────────────────────────────────────────────────
def page_framing():
    st.title("👑 챕터 2 — 팀장 정책")
    st.markdown("**상황**: 1주차 끝. 교수님이 팀장 자원자를 모집합니다.")

    if st.session_state.frame == "gain":
        st.success("📢 **교수님**: \"팀장 자원자에게 **+10점 가산**!\"")
    else:
        st.error("📢 **교수님**: \"팀장 안 맡으면 **-10점 차감**됩니다...\"")

    intent = st.radio(
        "🤚 자원하시겠습니까?",
        ["💯 적극 자원", "😊 의향 있음", "🤔 고민", "😐 별로", "🙅 절대 안 함"], index=2)

    deduct = st.select_slider(
        "💢 팀원이 무임승차하면 감점 발의?",
        ["전혀", "잘 안 함", "보통", "할듯", "당연히"], value="보통")

    if st.button("다음 →", type="primary", use_container_width=True):
        m_intent = {"💯 적극 자원": 7, "😊 의향 있음": 5, "🤔 고민": 4, "😐 별로": 2, "🙅 절대 안 함": 1}
        m_deduct = {"전혀": 1, "잘 안 함": 3, "보통": 4, "할듯": 5, "당연히": 7}

        st.session_state.answers.update(
            frame=st.session_state.frame,
            leader_intent=m_intent[intent],
            deduct_intent=m_deduct[deduct])

        # L vs G 측정
        if st.session_state.frame == "loss" and m_intent[intent] >= 5:
            add_score("L", 2)  # 손실 회피 강함
        elif st.session_state.frame == "gain" and m_intent[intent] >= 5:
            add_score("G", 2)  # 이득 추구 강함
        elif st.session_state.frame == "loss" and m_intent[intent] <= 3:
            add_score("G", 1)  # 손실 위협에도 안 흔들림 = 이득 추구형
        else:
            add_score("L", 1)
        next_step()


# ─────────────────────────────────────────────────
# 챕터 3: 팀 구성 (I vs A)
# ─────────────────────────────────────────────────
def page_team():
    st.title("👥 챕터 3 — 팀원 5명 선택")
    n = st.session_state.n_cand
    info = st.session_state.info_provided

    st.markdown(f"**상황**: 후보 **{n}명** 중 5명을 골라야 합니다.")

    if info:
        st.success("📋 **프로필 카드** 제공됨")
        rng = random.Random(42)
        skills = ["AI", "통계", "디자인", "발표", "코딩", "리서치", "관리"]
        cands = [{
            "이름": f"후보 {i+1}",
            "역량": rng.randint(5, 10),
            "관심": rng.choice(skills),
            "가용시간": rng.randint(1, 5),
            "경험": rng.choice(["많음", "보통", "적음"]),
        } for i in range(n)]
        st.dataframe(pd.DataFrame(cands), use_container_width=True, hide_index=True)
    else:
        st.warning("❗ **이름만** 알 수 있음")
        st.write(", ".join([f"후보 {i+1}" for i in range(n)]))

    st.markdown("---")

    style = st.radio(
        "🎯 어떻게 결정하시겠어요?",
        ["💭 직감으로 빠르게 5명 픽", "🔍 정보 다 비교한 후 신중히",
         "🤝 친한 사람부터 채워넣기", "📊 점수 매겨서 상위 5명"],
        index=1)

    sat = st.select_slider(
        "🎯 결과에 만족할까요?",
        ["😩 전혀", "😟 별로", "😐 그저", "🙂 만족", "🤩 매우"], value="😐 그저")

    redo = st.radio(
        "🔁 같은 상황 다시 와도 같은 결정?",
        ["✅ 예", "❌ 아니오"], horizontal=True)

    if st.button("다음 →", type="primary", use_container_width=True):
        m = {"😩 전혀": 1, "😟 별로": 2, "😐 그저": 4, "🙂 만족": 6, "🤩 매우": 7}
        st.session_state.answers.update(
            n_candidates=n, info_provided=info,
            decision_style=style, team_sat=m[sat],
            team_redo=("yes" if "예" in redo else "no"))

        # I vs A 측정
        if "직감" in style or "친한" in style:
            add_score("I", 2)
        else:
            add_score("A", 2)
        next_step()


# ─────────────────────────────────────────────────
# 챕터 4: 평가 체계 (D vs C)
# ─────────────────────────────────────────────────
def page_eval():
    st.title("📚 챕터 4 — 평가 체계")
    st.markdown("**상황**: 두 가지 평가 시스템에서 본인 학습 패턴을 예상해주세요.")

    st.markdown("### 📕 시나리오 A — *기말고사 1회 (40%)*")
    c1, c2 = st.columns(2)
    with c1:
        a8 = st.number_input("🌱 8주차 학습/주 (시간)", 0.0, 40.0, 5.0, 0.5, key="a8")
    with c2:
        a15 = st.number_input("🔥 15주차 학습/주", 0.0, 40.0, 15.0, 0.5, key="a15")

    st.markdown("### 📗 시나리오 B — *격주 퀴즈 6회 + 기말 40%*")
    c1, c2 = st.columns(2)
    with c1:
        b8 = st.number_input("🌱 8주차", 0.0, 40.0, 7.0, 0.5, key="b8")
    with c2:
        b15 = st.number_input("🔥 15주차", 0.0, 40.0, 12.0, 0.5, key="b15")

    pref = st.radio(
        "📌 둘 중 어떤 평가가 본인에게 더 잘 맞을 것 같아요?",
        ["📕 단일 기말 (집중 폭발)", "📗 격주 퀴즈 (꾸준 분산)"], horizontal=True)

    if st.button("다음 →", type="primary", use_container_width=True):
        st.session_state.answers.update(
            single_w8=a8, single_w15=a15, biweek_w8=b8, biweek_w15=b15, eval_pref=pref)

        # D vs C 측정
        # 단일 기말의 학기말 폭발이 클수록 C형
        cramming = a15 - a8
        spreading = b15 - b8
        if cramming > spreading + 3 or "단일" in pref:
            add_score("C", 2)
        else:
            add_score("D", 2)
        next_step()


# ─────────────────────────────────────────────────
# 챕터 5: 마무리
# ─────────────────────────────────────────────────
def page_final():
    st.title("🎬 챕터 5 — 마무리")

    overall = st.slider("🎓 IMEN315 강의계획서 만족도", 1, 7, 4)
    influence = st.slider("✨ 강의계획서가 행동에 영향?", 1, 7, 4)
    free = st.text_area("✍️ 자유 의견 (선택)", height=80)
    contact = st.text_input("☕ 추첨 연락처 (선택)")

    if st.button("🧬 결과 보기", type="primary", use_container_width=True):
        st.session_state.answers.update(
            overall=overall, influence=influence, free=free, contact=contact,
            timestamp=datetime.now().isoformat(),
            scores=str(st.session_state.scores))
        try:
            save_response(st.session_state.answers)
        except Exception:
            pass
        next_step()


# ─────────────────────────────────────────────────
# 챕터 6: 학습 MBTI 결과
# ─────────────────────────────────────────────────
def page_result():
    s = st.session_state.scores

    # 4 글자 결정
    code = ""
    code += "L" if s["L"] >= s["G"] else "G"
    code += "P" if s["P"] >= s["R"] else "R"
    code += "D" if s["D"] >= s["C"] else "C"
    code += "I" if s["I"] >= s["A"] else "A"

    profile = TYPE_PROFILES.get(code, {"emoji": "❓", "name": "분석 중", "desc": ""})

    st.balloons()
    st.markdown(
        f"""
        <div style="text-align:center;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
        color:white;padding:32px 16px;border-radius:16px;margin:8px 0">
        <div style="font-size:0.9em;opacity:0.85">당신의 학습 MBTI</div>
        <div style="font-size:4em;line-height:1.1;margin:8px 0">{profile['emoji']}</div>
        <div style="font-size:3em;font-weight:800;letter-spacing:0.15em">{code}</div>
        <div style="font-size:1.6em;margin-top:8px">{profile['name']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**해설**: {profile['desc']}")

    st.markdown("---")
    st.subheader("📊 4가지 차원 점수")

    dim_data = []
    for label, l1, l2, name1, name2 in DIMENSIONS:
        v1, v2 = s[l1], s[l2]
        total = v1 + v2 if (v1 + v2) > 0 else 1
        pct1 = round(100 * v1 / total)
        pct2 = 100 - pct1
        winner = l1 if v1 >= v2 else l2
        dim_data.append({
            "차원": label,
            f"{l1} ({name1})": pct1,
            f"{l2} ({name2})": pct2,
            "결과": winner,
        })

    for d in dim_data:
        cols = st.columns([1, 4, 1])
        with cols[0]:
            st.write(f"**{d['차원']}**")
        with cols[1]:
            keys = list(d.keys())
            left_key, right_key = keys[1], keys[2]
            left_val, right_val = d[left_key], d[right_key]
            st.write(f"{left_key} **{left_val}%** ⬛ — {right_key} **{right_val}%**")
            st.progress(left_val / 100)
        with cols[2]:
            st.metric("", d["결과"])

    st.markdown("---")
    st.subheader("🧬 16가지 유형 (당신은 강조)")

    grid = []
    codes = list(TYPE_PROFILES.keys())
    for i in range(0, 16, 4):
        row = []
        for c in codes[i:i+4]:
            p = TYPE_PROFILES[c]
            mark = "🌟" if c == code else "·"
            row.append(f"{mark} {p['emoji']} **{c}**\n{p['name']}")
        grid.append(row)

    for row in grid:
        cols = st.columns(4)
        for col, item in zip(cols, row):
            col.markdown(item)

    st.markdown("---")

    # 인간공학 인사이트
    a = st.session_state.answers
    if a.get("frame") == "loss" and a.get("leader_intent", 0) >= 5:
        st.info(
            "💡 **흥미로운 발견** — 당신은 '-10점 차감' 시나리오에서 자원 의도가 높았어요. "
            "이건 **Prospect Theory(Tversky & Kahneman)**가 예측한 인류 평균 — "
            "사람은 손실을 이득보다 약 2배 강하게 느낍니다. 당신은 이 효과에 강하게 반응."
        )

    cramming = a.get("single_w15", 0) - a.get("single_w8", 0)
    if cramming > 5:
        st.warning(
            f"⚠️ **벼락치기 패턴 감지** — 단일 기말 시나리오에서 학기말 학습이 {cramming:.0f}h 증가. "
            "이는 **Forgetting Curve (Ebbinghaus 1885)**가 예측하는 비효율 패턴이에요. "
            "분산 학습이 인출 시간을 약 3.4배 단축한다는 시뮬 결과 있음."
        )

    st.markdown("---")
    st.success(
        "🙇 **응답 감사합니다!** 결과는 6/12 보고서 제출 후 단톡에 익명 요약 공유. "
        "기프티콘 추첨은 6/3 발표."
    )

    st.caption(f"_(분석 기반: 응답 데이터 → 4 차원 점수 → 16 유형 매핑. 자세한 이론은 [GitHub](https://github.com/lshpy/imen315-syllabus-meta) 참고)_")

    if st.button("🔁 다른 친구 권유하기 (처음부터)"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ─────────────────────────────────────────────────
# 라우팅
# ─────────────────────────────────────────────────
PAGES = [page_intro, page_attendance, page_framing, page_team,
         page_eval, page_final, page_result]
PAGES[min(st.session_state.step, len(PAGES) - 1)]()
