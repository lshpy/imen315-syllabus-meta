"""게임형 설문 앱 (Streamlit) — 응답 후 본인 결과 즉시 시각화

사용:
    pip install streamlit pandas
    streamlit run team_project/survey/streamlit_app.py

배포:
    Streamlit Cloud (무료) — share.streamlit.io 에서 GitHub repo 연결
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="IMEN315 강의계획서 인식 조사", page_icon="🧠", layout="centered")

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
# 진행률
# ─────────────────────────────────────────────────
TOTAL_STEPS = 6
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}

st.progress(st.session_state.step / TOTAL_STEPS)
st.caption(f"진행 {st.session_state.step}/{TOTAL_STEPS}")


# ─────────────────────────────────────────────────
# 0. 도입
# ─────────────────────────────────────────────────
def page_intro():
    st.title("🧠 IMEN315 강의계획서 인식 조사")
    st.write(
        "안녕하세요! IMEN315 인간공학 수강생입니다.\n\n"
        "강의계획서가 학생 행동에 어떤 영향을 주는지 분석하고 있어요. "
        "**5분이면 끝**나고, 모든 답변은 **익명**으로 처리됩니다.\n\n"
        "🎁 완료자 중 추첨으로 **스타벅스 기프티콘 5장** 드립니다."
    )
    if st.button("시작하기 →", type="primary"):
        st.session_state.step = 1
        st.rerun()


# ─────────────────────────────────────────────────
# 1. 본인 정보
# ─────────────────────────────────────────────────
def page_demographics():
    st.header("1. 본인에 대해")
    grade = st.radio("학년", ["1학년", "2학년", "3학년", "4학년", "졸업유예·기타"])
    dept = st.text_input("소속 학과", "산업경영공학부")
    gpa = st.select_slider(
        "직전 학기 학점",
        options=["3.0 미만", "3.0–3.5", "3.5–4.0", "4.0 이상", "응답 안 함"],
        value="3.5–4.0",
    )
    attend = st.select_slider(
        "평소 출석률",
        options=["60% 미만", "60–80%", "80–95%", "95% 이상"],
        value="80–95%",
    )
    if st.button("다음 →"):
        st.session_state.answers.update(
            grade=grade, dept=dept, gpa=gpa, self_attend=attend
        )
        st.session_state.step = 2
        st.rerun()


# ─────────────────────────────────────────────────
# 2. 출석 가상 상황
# ─────────────────────────────────────────────────
def page_attendance():
    st.header("2. 출석 체크 가상 상황")
    st.write("아래 3가지 상황을 보고 본인이 어떻게 행동할지 답해주세요.")

    st.subheader("📅 상황 A — 매주 월요일에만 체크")
    a_skip = st.slider("결석할 의도? (1=없음 ~ 7=매우 큼)", 1, 7, 4, key="a_skip")
    a_rain = st.slider("비 오는 날에도 갈 가능성? (%)", 0, 100, 50, key="a_rain")

    st.subheader("🎲 상황 B — 30회 중 7회 무작위, 횟수는 알려줌")
    b_skip = st.slider("결석할 의도?", 1, 7, 4, key="b_skip")
    b_rain = st.slider("비 오는 날 갈 가능성? (%)", 0, 100, 50, key="b_rain")

    st.subheader("🌫️ 상황 C — 무작위 + 횟수도 안 알려줌")
    c_skip = st.slider("결석할 의도?", 1, 7, 4, key="c_skip")
    c_rain = st.slider("비 오는 날 갈 가능성? (%)", 0, 100, 50, key="c_rain")

    check = st.radio(
        "위 세 상황 중 가장 예측 불가능한 건?",
        ["A", "B", "C"],
        index=2,
    )

    if st.button("다음 →"):
        st.session_state.answers.update(
            attend_A_skip=a_skip, attend_A_rain=a_rain,
            attend_B_skip=b_skip, attend_B_rain=b_rain,
            attend_C_skip=c_skip, attend_C_rain=c_rain,
            attend_check=check,
        )
        st.session_state.step = 3
        st.rerun()


# ─────────────────────────────────────────────────
# 3. 팀장 인센티브 (Framing) — 무작위 분기
# ─────────────────────────────────────────────────
def page_framing():
    st.header("3. 팀장 정책")

    import random
    if "frame" not in st.session_state:
        st.session_state.frame = random.choice(["gain", "loss"])

    if st.session_state.frame == "gain":
        st.info("**팀장 자원 시 최대 +10점 가산**")
    else:
        st.warning("**팀장 안 맡으면 평균에서 최대 -10점 차감**")

    intent = st.slider("팀장 지원할 의도?", 1, 7, 4)
    deduct = st.slider("기여 부족 시 감점 발의 의도?", 1, 7, 4)
    feel = st.slider("이 정책 어떻게 느낌? (1=부정 ~ 7=긍정)", 1, 7, 4)

    if st.button("다음 →"):
        st.session_state.answers.update(
            frame=st.session_state.frame,
            leader_intent=intent, deduct_intent=deduct, frame_feel=feel,
        )
        st.session_state.step = 4
        st.rerun()


# ─────────────────────────────────────────────────
# 4. 팀 구성
# ─────────────────────────────────────────────────
def page_team():
    st.header("4. 5명 팀 구성")
    import random
    if "n_cand" not in st.session_state:
        st.session_state.n_cand = random.choice([3, 7, 15])
        st.session_state.info_provided = random.choice([True, False])

    n = st.session_state.n_cand
    info = st.session_state.info_provided
    st.write(f"**후보 {n}명**에서 5명 팀을 구성한다고 가정해보세요. "
             f"({'정보 제공' if info else '이름만 제공'})")

    sat = st.slider("선택했을 때 만족도?", 1, 7, 4)
    better = st.slider("더 좋은 선택이 있을 것 같은가?", 1, 7, 4)
    redo = st.radio("같은 팀 다시 고를 의향?", ["예", "아니오"])

    if st.button("다음 →"):
        st.session_state.answers.update(
            n_candidates=n, info_provided=info,
            team_sat=sat, team_better=better, team_redo=redo,
        )
        st.session_state.step = 5
        st.rerun()


# ─────────────────────────────────────────────────
# 5. 평가 체계
# ─────────────────────────────────────────────────
def page_eval():
    st.header("5. 평가 체계와 학습시간")

    st.subheader("📚 단일 기말 (40%)")
    a8 = st.number_input("8주차 학습시간/주 (시간)", 0.0, 40.0, 5.0, step=0.5, key="a8")
    a15 = st.number_input("15주차 학습시간/주 (시간)", 0.0, 40.0, 15.0, step=0.5, key="a15")

    st.subheader("📝 격주 퀴즈 6회 + 기말 40%")
    b8 = st.number_input("8주차 학습시간/주 (시간)", 0.0, 40.0, 7.0, step=0.5, key="b8")
    b15 = st.number_input("15주차 학습시간/주 (시간)", 0.0, 40.0, 12.0, step=0.5, key="b15")

    if st.button("다음 →"):
        st.session_state.answers.update(
            single_w8=a8, single_w15=a15,
            biweek_w8=b8, biweek_w15=b15,
        )
        st.session_state.step = 6
        st.rerun()


# ─────────────────────────────────────────────────
# 6. 마무리 + 결과 시각화
# ─────────────────────────────────────────────────
def page_result():
    st.header("6. 마무리")
    overall = st.slider("강의계획서 만족도", 1, 7, 4)
    influence = st.slider("강의계획서가 행동에 영향을 줬다고 생각?", 1, 7, 4)
    free = st.text_area("자유 의견 (선택)", "")
    contact = st.text_input("기프티콘 추첨 연락처 (선택)", "")

    if st.button("제출하고 결과 보기 ✨", type="primary"):
        st.session_state.answers.update(
            overall=overall, influence=influence, free=free, contact=contact,
            timestamp=datetime.now().isoformat(),
        )
        try:
            save_response(st.session_state.answers)
        except Exception as e:
            st.warning(f"저장 실패 (무시 가능): {e}")
        st.session_state.step = 7
        st.rerun()


def page_done():
    st.balloons()
    st.success("🎉 응답 완료! 감사합니다.")
    st.write("---")
    st.subheader("🔍 본인 응답 요약")

    a = st.session_state.answers

    # 출석 요약
    skip_avg = (a.get("attend_A_skip", 0) + a.get("attend_B_skip", 0) + a.get("attend_C_skip", 0)) / 3
    if a.get("attend_C_skip", 7) < a.get("attend_A_skip", 0):
        msg = "⚡ 무작위 + 비공개일 때 결석 의도가 가장 낮네요. **가변비율 강화 효과**가 보입니다 (Skinner 원리)."
    else:
        msg = "🎲 출석 정책에 큰 영향을 받지 않는 편이네요."
    st.info(f"**출석 의도 평균** {skip_avg:.1f}/7 — {msg}")

    # Framing
    frame = a.get("frame")
    intent = a.get("leader_intent", 0)
    if frame == "gain" and intent >= 5:
        st.info(f"💰 **이득 표현(+10)에 강하게 반응** — 동기 부여형이에요.")
    elif frame == "loss" and intent >= 5:
        st.info(f"⚠️ **손실 표현(-10)에 강하게 반응** — 손실 회피형 (대다수 사람이 이쪽).")

    # 학습시간 분산
    single_var = abs(a.get("single_w15", 0) - a.get("single_w8", 0))
    biweek_var = abs(a.get("biweek_w15", 0) - a.get("biweek_w8", 0))
    st.info(
        f"📚 **단일 기말 학습시간 격차** {single_var:.1f}h vs **격주 퀴즈** {biweek_var:.1f}h\n"
        + ("→ 단일 기말일 때 학기말 벼락치기 경향" if single_var > biweek_var else "→ 평가 체계와 무관하게 일정 학습 패턴")
    )

    st.write("---")
    st.write(
        "결과는 **6/12 LMS 보고서 제출 후** IMEN315 단톡에 익명 요약으로 공유됩니다.\n"
        "기프티콘 추첨은 **6/3 발표** 예정."
    )
    if st.button("다시 시작"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ─────────────────────────────────────────────────
# 라우팅
# ─────────────────────────────────────────────────
PAGES = [page_intro, page_demographics, page_attendance,
         page_framing, page_team, page_eval, page_result, page_done]
PAGES[st.session_state.step]()
