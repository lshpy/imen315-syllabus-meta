"""IMEN315 강의계획서 인식 조사 — 인터랙티브 스토리 게임
'당신은 IMEN315 수강생입니다' 형식으로 진행되는 선택형 설문.

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
    page_title="IMEN315 학기 시뮬레이터",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path(__file__).parent / "data" / "streamlit_responses.csv"
DATA_FILE.parent.mkdir(exist_ok=True)


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
    st.session_state.traits = {"risk_avoid": 0, "memory_load": 0, "social_bias": 0}


def next_step():
    st.session_state.step += 1
    st.rerun()


def chip(text: str, color: str = "gray") -> str:
    palettes = {
        "gray": "#e9ecef",
        "blue": "#a5d8ff",
        "green": "#b2f2bb",
        "yellow": "#ffec99",
        "red": "#ffc9c9",
        "purple": "#d0bfff",
    }
    bg = palettes.get(color, "#e9ecef")
    return f'<span style="background:{bg};padding:3px 10px;border-radius:12px;font-size:0.85em">{text}</span>'


# 진행률
TOTAL = 7
if st.session_state.step > 0 and st.session_state.step < TOTAL:
    st.progress(st.session_state.step / (TOTAL - 1))
    st.caption(f"📖 챕터 {st.session_state.step} / {TOTAL - 1}")


# ─────────────────────────────────────────────────
# 챕터 0: 인트로 (스토리 시작)
# ─────────────────────────────────────────────────
def page_intro():
    st.title("🎓 IMEN315 학기 시뮬레이터")
    st.markdown(
        """
        ### 당신은 IMEN315 인간공학 수강생입니다.

        오늘은 학기 첫날 — 강의계획서를 받아 들었습니다.

        > *"이 수업의 평가는 출석 10%, 기말 40%, 팀과제 50% 입니다.*
        > *출석은 무작위로 체크되고, 팀장 자원자에겐 +10점, 무임승차하면 -10점이 차감됩니다..."*

        **앞으로 한 학기 동안 당신은 어떤 선택을 할까요?**

        7개의 갈림길에서 본인의 행동을 골라주세요. 끝나면 **당신의 학습 패턴 유형**이 분석됩니다.

        ⏱️ 약 5분 · 🎁 완료자 추첨 스타벅스 5장 · 🔒 익명
        """
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.session_state.answers["nickname"] = st.text_input(
            "🧑 캐릭터 닉네임 (익명)", value="익명의 수강생", max_chars=20
        )
    with col2:
        st.session_state.answers["grade"] = st.selectbox(
            "학년", ["1학년", "2학년", "3학년", "4학년", "기타"]
        )

    if st.button("📜 학기 시작 →", type="primary", use_container_width=True):
        next_step()


# ─────────────────────────────────────────────────
# 챕터 1: 출석 (3 시나리오 비교)
# ─────────────────────────────────────────────────
def page_attendance():
    st.title("📅 챕터 1 — 출석의 갈림길")

    st.info(
        "**상황**: 비 오는 화요일 아침. 일어나서 수업을 갈지 말지 고민 중.\n\n"
        "**같은 비 오는 날인데, 아래 3가지 수업의 출석 정책이 다릅니다.** 각 상황에서 **결석 충동**을 표시해주세요."
    )

    st.markdown("---")
    st.markdown("### 🌧️ 시나리오 A — *매주 월요일에만 출석 체크*")
    st.caption("→ 화요일은 어차피 안 부름. 그래도 갈까?")
    a = st.select_slider(
        "결석 충동",
        options=["😴 절대 안 감", "😪 안 가고 싶음", "🤔 모르겠음", "🙂 갈까 말까", "🏃 갈래"],
        value="🤔 모르겠음",
        key="attend_A",
    )

    st.markdown("---")
    st.markdown("### 🎲 시나리오 B — *30회 중 7회를 무작위로 체크 (횟수는 알려줌)*")
    st.caption("→ 7번이라는 건 알지만 언제일진 모름")
    b = st.select_slider(
        "결석 충동",
        options=["😴 절대 안 감", "😪 안 가고 싶음", "🤔 모르겠음", "🙂 갈까 말까", "🏃 갈래"],
        value="🤔 모르겠음",
        key="attend_B",
    )

    st.markdown("---")
    st.markdown("### 🌫️ 시나리오 C — *무작위 + 횟수도 안 알려줌*")
    st.caption("→ 몇 번인지 아예 모름. 매번 체크 가능")
    c = st.select_slider(
        "결석 충동",
        options=["😴 절대 안 감", "😪 안 가고 싶음", "🤔 모르겠음", "🙂 갈까 말까", "🏃 갈래"],
        value="🤔 모르겠음",
        key="attend_C",
    )

    st.markdown("---")
    st.markdown("**🔍 이해 확인** — 위 셋 중 가장 예측 불가능한 시나리오는?")
    check = st.radio("선택", ["A", "B", "C"], index=2, horizontal=True, key="attend_check")

    if st.button("다음 챕터 →", type="primary", use_container_width=True):
        scale_map = {"😴 절대 안 감": 1, "😪 안 가고 싶음": 2, "🤔 모르겠음": 3, "🙂 갈까 말까": 4, "🏃 갈래": 5}
        st.session_state.answers.update(
            attend_A=scale_map[a],
            attend_B=scale_map[b],
            attend_C=scale_map[c],
            attend_check=check,
        )
        # 손실회피 성향 측정 (C에서 가장 적게 결석할수록 가변강화에 반응)
        if scale_map[c] >= scale_map[a]:
            st.session_state.traits["risk_avoid"] += 1
        next_step()


# ─────────────────────────────────────────────────
# 챕터 2: 팀장 인센티브 (Framing)
# ─────────────────────────────────────────────────
def page_framing():
    st.title("👑 챕터 2 — 팀장이 되시겠습니까?")

    st.markdown(
        "**상황**: 1주차 수업이 끝났습니다. 교수님이 팀장 자원자를 모집합니다.\n\n"
        "교수님 메시지에 따라 당신의 마음은 어떻게 움직일까요?"
    )

    if st.session_state.frame == "gain":
        st.success(
            "📢 **교수님**: \n"
            "> *\"팀장 자원자에게는 최대 **+10점이 가산**됩니다. 좋은 기회입니다!\"*"
        )
    else:
        st.error(
            "📢 **교수님**: \n"
            "> *\"누군가는 팀장을 해야 합니다. **자원하지 않으면** 무작위로 배정되며, "
            "팀장 책임을 다하지 못한 경우 **최대 -10점이 차감**됩니다.\"*"
        )

    st.markdown("---")

    intent = st.radio(
        "🤚 팀장 자원하시겠습니까?",
        ["💯 적극 자원!", "😊 자원할 의향 있음", "🤔 고민 중", "😐 안 하고 싶음", "🙅 절대 안 함"],
        index=2,
    )
    intent_map = {
        "💯 적극 자원!": 7, "😊 자원할 의향 있음": 5, "🤔 고민 중": 4,
        "😐 안 하고 싶음": 2, "🙅 절대 안 함": 1,
    }

    st.markdown("---")

    deduct = st.select_slider(
        "💢 만약 팀원이 무임승차하면, 적극 감점 발의할 의향?",
        options=["전혀 안 함", "잘 안 함", "보통", "할 것 같음", "당연히 함"],
        value="보통",
    )
    deduct_map = {"전혀 안 함": 1, "잘 안 함": 3, "보통": 4, "할 것 같음": 5, "당연히 함": 7}

    if st.button("다음 챕터 →", type="primary", use_container_width=True):
        st.session_state.answers.update(
            frame=st.session_state.frame,
            leader_intent=intent_map[intent],
            deduct_intent=deduct_map[deduct],
        )
        if st.session_state.frame == "loss" and intent_map[intent] >= 5:
            st.session_state.traits["risk_avoid"] += 2
        next_step()


# ─────────────────────────────────────────────────
# 챕터 3: 팀 구성 (Satisficing)
# ─────────────────────────────────────────────────
def page_team():
    st.title("👥 챕터 3 — 운명의 팀원 5명")

    n = st.session_state.n_cand
    info = st.session_state.info_provided

    st.markdown(
        f"**상황**: 당신은 팀장이 되었습니다. **{n}명의 후보** 중 5명을 골라 팀을 만들어야 합니다."
    )

    if info:
        st.success("📋 학과에서 후보별 **프로필 카드**를 제공했습니다 (역량·시간·관심·경험)")
    else:
        st.warning("❗ **이름만** 알 수 있습니다. 다른 정보는 없음.")

    st.markdown("---")

    # 가상 후보 생성 + 표시
    rng = random.Random(42)
    candidates = []
    skills = ["AI", "통계", "디자인", "발표", "코딩", "리서치", "관리"]
    for i in range(n):
        cand = {
            "name": f"후보 {i+1}",
            "역량": rng.randint(5, 10),
            "관심": rng.choice(skills),
            "가용시간": rng.randint(1, 5),
            "경험": rng.choice(["많음", "보통", "적음"]),
        }
        candidates.append(cand)

    if info:
        df_show = pd.DataFrame(candidates)
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.write(", ".join([c["name"] for c in candidates]))

    st.markdown("---")

    sat = st.select_slider(
        "🎯 5명을 머릿속으로 골라봤다고 가정. **만족스럽나요?**",
        options=["😩 전혀", "😟 별로", "😐 그저그럼", "🙂 만족", "🤩 매우 만족"],
        value="😐 그저그럼",
    )
    sat_map = {"😩 전혀": 1, "😟 별로": 2, "😐 그저그럼": 4, "🙂 만족": 6, "🤩 매우 만족": 7}

    better = st.radio(
        "🤔 더 좋은 조합이 있을 것 같다는 생각?",
        ["💭 그렇다 (시간 더 있으면 다시 고민할 듯)", "👌 아니다 (이 정도면 충분)"],
    )

    redo = st.radio(
        "🔁 똑같은 상황 다시 와도 같은 팀 고를 의향?",
        ["✅ 예", "❌ 아니오"],
        horizontal=True,
    )

    if st.button("다음 챕터 →", type="primary", use_container_width=True):
        st.session_state.answers.update(
            n_candidates=n,
            info_provided=info,
            team_sat=sat_map[sat],
            team_better=("better" if "그렇다" in better else "ok"),
            team_redo=("yes" if "예" in redo else "no"),
        )
        if n >= 8 and not info:
            st.session_state.traits["memory_load"] += 2
        next_step()


# ─────────────────────────────────────────────────
# 챕터 4: 평가 체계 (Forgetting Curve)
# ─────────────────────────────────────────────────
def page_eval():
    st.title("📚 챕터 4 — 두 갈래의 평가")

    st.markdown(
        "**상황**: 수업이 진행 중. 두 가지 평가 체계가 있다고 가정해봅시다.\n\n"
        "각 시스템에서 **본인의 학습 패턴**이 어떨지 예상해주세요."
    )

    st.markdown("---")

    st.markdown("### 📕 시나리오 A — *기말고사 1회 (40%)*")
    col1, col2 = st.columns(2)
    with col1:
        a8 = st.number_input("🌱 8주차 (학기 중반) 학습/주", 0.0, 40.0, 5.0, 0.5, key="a8",
                             help="시간 단위")
    with col2:
        a15 = st.number_input("🔥 15주차 (학기말) 학습/주", 0.0, 40.0, 15.0, 0.5, key="a15")

    st.markdown("---")

    st.markdown("### 📗 시나리오 B — *격주 퀴즈 6회 + 기말 40%*")
    col1, col2 = st.columns(2)
    with col1:
        b8 = st.number_input("🌱 8주차 학습/주", 0.0, 40.0, 7.0, 0.5, key="b8")
    with col2:
        b15 = st.number_input("🔥 15주차 학습/주", 0.0, 40.0, 12.0, 0.5, key="b15")

    if st.button("다음 챕터 →", type="primary", use_container_width=True):
        st.session_state.answers.update(
            single_w8=a8, single_w15=a15, biweek_w8=b8, biweek_w15=b15,
        )
        if a15 - a8 > 5:  # 학기말 벼락치기 패턴
            st.session_state.traits["memory_load"] += 1
        next_step()


# ─────────────────────────────────────────────────
# 챕터 5: 마무리 + 자유 의견
# ─────────────────────────────────────────────────
def page_final():
    st.title("🎬 챕터 5 — 학기를 돌아보며")

    overall = st.slider("🎓 IMEN315 강의계획서, 전체적으로 만족스럽나요?", 1, 7, 4)
    influence = st.slider("✨ 강의계획서가 본인 행동에 영향 줬다고 느끼시나요?", 1, 7, 4)

    surprise = st.text_input("💡 가장 의외였던 규칙 한 가지 (선택)", placeholder="예: 무작위 출석 체크")
    free = st.text_area("✍️ 자유 의견 (선택)", placeholder="더 나은 강의계획서가 되려면...", height=100)
    contact = st.text_input("☕ 기프티콘 추첨 연락처 (선택)", placeholder="이메일 또는 카톡 ID")

    if st.button("✨ 결과 분석하기", type="primary", use_container_width=True):
        st.session_state.answers.update(
            overall=overall, influence=influence, surprise=surprise,
            free=free, contact=contact, timestamp=datetime.now().isoformat(),
        )
        try:
            save_response(st.session_state.answers)
        except Exception:
            pass
        next_step()


# ─────────────────────────────────────────────────
# 챕터 6: 결과 분석
# ─────────────────────────────────────────────────
def page_result():
    st.title("🏆 결과: 당신의 학습 유형")
    st.balloons()

    a = st.session_state.answers
    t = st.session_state.traits

    # 유형 판정
    if t["risk_avoid"] >= 2:
        type_name = "🛡️ 손실 회피형 학습자"
        type_desc = (
            "당신은 **+점수 가산**보다 **-점수 차감**에 더 강하게 반응하는 타입.\n"
            "프로스펙트 이론(Tversky & Kahneman)이 예측한 인류 평균 패턴이에요. "
            "'잃는 게 무서워서' 매일 출석하고 책임을 진다면 — 그게 인간공학이 말하는 **손실 회피**입니다."
        )
        color = "blue"
    elif t["memory_load"] >= 2:
        type_name = "🧠 작업기억 한계형"
        type_desc = (
            "당신은 정보가 많아질수록 (후보 8명+, 학기 14주+) **'그럭저럭 괜찮은' 선택**으로 "
            "수렴하는 패턴을 보입니다 — Simon의 만족화(Satisficing)와 일치.\n"
            "이건 약점이 아니라 **인간 보편적 인지 한계**예요. 이를 보완하는 인터페이스 설계가 인간공학의 핵심."
        )
        color = "purple"
    else:
        type_name = "🎯 균형 학습자"
        type_desc = (
            "당신은 강의계획서 정책의 영향을 비교적 **덜 받는** 타입.\n"
            "강한 자기조절력이나 명확한 개인 전략이 있는 경우입니다. "
            "이런 학생들이 평균을 보정하는 중요한 변수예요."
        )
        color = "green"

    # 유형 카드
    st.markdown(
        f"""
        <div style="background:#f8f9fa;border-left:6px solid #4dabf7;padding:18px;border-radius:8px;margin:12px 0">
        <h2 style="margin-top:0">{type_name}</h2>
        <p style="font-size:1.05em;line-height:1.6">{type_desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("📊 본인 응답 vs 이론 예측")

    col1, col2, col3 = st.columns(3)
    with col1:
        diff = a.get("attend_A", 3) - a.get("attend_C", 3)
        match = "✅ 일치" if diff > 0 else "❌ 어긋남"
        st.metric("출석 정책 영향", f"{diff:+d}", help="A(고정) - C(무작위)")
        st.caption(f"가변강화 이론 {match}")

    with col2:
        cramming = a.get("single_w15", 0) - a.get("single_w8", 0)
        spread = a.get("biweek_w15", 0) - a.get("biweek_w8", 0)
        match = "✅ 일치" if cramming > spread else "❌ 어긋남"
        st.metric("학기말 벼락치기", f"+{cramming:.0f}h",
                  help="단일기말 vs 격주퀴즈 학기말 학습 증가")
        st.caption(f"망각 곡선 {match}")

    with col3:
        n = a.get("n_candidates", 7)
        sat = a.get("team_sat", 4)
        st.metric("팀 구성 만족", f"{sat}/7", help=f"후보 {n}명")
        st.caption("작업기억 7±2")

    st.markdown("---")

    if a.get("frame") == "loss" and a.get("leader_intent", 0) >= 5:
        st.info(
            "💡 **흥미로운 사실** — 당신은 '-10점 차감' 시나리오를 봤고, **자원 의도가 높았어요**. "
            "교수님이 동일한 정책을 '+10 가산' 표현으로 보여줬다면 의도가 더 낮았을 가능성이 큽니다 "
            "(Framing Effect, 손실 회피 ≈ 이득 추구 × 2)."
        )
    elif a.get("frame") == "gain" and a.get("leader_intent", 0) >= 5:
        st.info(
            "💡 **흥미로운 사실** — 당신은 '+10점 가산' 시나리오를 봤고, 자원 의도가 높았어요. "
            "이런 분은 인구 중 약 30%로, 이득 추구형 (gain-seeker) 패턴입니다."
        )

    st.markdown("---")
    st.success(
        "🙇 **감사합니다!** 응답은 6/12 LMS 보고서 제출 후 단톡에 익명 요약으로 공유돼요.\n"
        "기프티콘 추첨은 6/3 발표."
    )

    if st.button("🔁 처음부터 다시"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ─────────────────────────────────────────────────
# 라우팅
# ─────────────────────────────────────────────────
PAGES = [page_intro, page_attendance, page_framing, page_team,
         page_eval, page_final, page_result]
PAGES[min(st.session_state.step, len(PAGES) - 1)]()
