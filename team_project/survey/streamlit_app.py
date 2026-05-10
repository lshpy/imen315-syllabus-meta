"""IMEN315 강의계획서 인식 조사 — 학습 MBTI 게임"""
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
# 16가지 학습 MBTI
# ─────────────────────────────────────────────────
DIMENSIONS = [
    ("동기", "L", "G", "손실 회피", "이득 추구"),
    ("환경", "P", "R", "예측 가능", "무작위 적응"),
    ("학습", "D", "C", "분산 학습", "집중 학습"),
    ("결정", "I", "A", "직관 결정", "분석 결정"),
]

TYPES = {
    "LPDA": {"emoji": "🛡️", "name": "안정의 분석가", "color": "#4dabf7",
             "desc": "위험 피하고 예측 가능한 환경에서 꾸준히 분산 학습 + 체계적 분석. 가장 모범적이지만 변화에 약할 수 있음."},
    "LPDI": {"emoji": "📚", "name": "성실한 직관가", "color": "#74c0fc",
             "desc": "안정 환경 + 분산 학습 + 빠른 결정. 직관 의존. 균형 잡힌 학생."},
    "LPCA": {"emoji": "🎯", "name": "기말 집중 전략가", "color": "#3bc9db",
             "desc": "안정 추구 + 학기말 집중 + 분석. 평소 살살 + 시험 직전 폭발."},
    "LPCI": {"emoji": "🦔", "name": "안전한 벼락치기형", "color": "#66d9e8",
             "desc": "고정 환경 좋아하지만 분산 학습 못 함. 직관 + 벼락치기. 흔한 한국 대학생 표준."},
    "LRDA": {"emoji": "🦉", "name": "신중한 적응 학자", "color": "#5c7cfa",
             "desc": "변화에 적응 + 손실 회피 + 분산 학습 + 분석. 매우 견고."},
    "LRDI": {"emoji": "🐺", "name": "본능적 생존가", "color": "#7950f2",
             "desc": "무작위 환경에서도 분산 학습으로 살아남음. 직관 의존. 위기 대응력 최강."},
    "LRCA": {"emoji": "🎮", "name": "벼락치기 분석가", "color": "#9775fa",
             "desc": "변동성 적응 + 학기말 집중 + 분석. 단기 폭발력 최고. 평소엔 게이밍."},
    "LRCI": {"emoji": "🐌", "name": "도전 회피형 벼락치기", "color": "#b197fc",
             "desc": "변화는 받아들이지만 분산 못 하고 직관 의존. 운에 의존."},
    "GPDA": {"emoji": "🚀", "name": "동기부여형 모범생", "color": "#51cf66",
             "desc": "이득 추구 + 안정 + 분산 + 분석. 가산점에 강하게 반응 + 체계적. 이상적."},
    "GPDI": {"emoji": "⚡", "name": "직진 학습자", "color": "#69db7c",
             "desc": "이득 보고 달려가며 안정 + 분산. 직관. 빠르고 효율적."},
    "GPCA": {"emoji": "🦅", "name": "기말 폭격기", "color": "#94d82d",
             "desc": "이득 + 안정 + 학기말 집중 + 분석. 효율 추구."},
    "GPCI": {"emoji": "🐯", "name": "타고난 벼락치기 천재", "color": "#fcc419",
             "desc": "이득 + 직관 + 집중. 평균 이상 거두지만 운 변수 큼."},
    "GRDA": {"emoji": "🐉", "name": "전천후 도전가", "color": "#ff922b",
             "desc": "이득 + 변동성 + 분산 + 분석. 어떤 환경에서도 적응. 리더형."},
    "GRDI": {"emoji": "🔥", "name": "직진 모험가", "color": "#ff6b6b",
             "desc": "이득 + 변화 즐김 + 분산 + 직관. 활동량 최고."},
    "GRCA": {"emoji": "🎲", "name": "도박형 천재", "color": "#f06595",
             "desc": "이득 + 변동성 + 학기말 집중 + 분석. 위험 감수 + 폭발력. 결과 양극화."},
    "GRCI": {"emoji": "🌪️", "name": "감각적 직관파", "color": "#cc5de8",
             "desc": "이득 + 변동성 + 집중 + 직관. 감으로 살지만 묘하게 잘됨."},
}

# 가상 후보 풀 — 친밀도(closeness) × 역량(ability) 트레이드오프 설계
# satisficing 측정: 친분 높은 후보는 역량 중간, 역량 최고는 친분 낮음
# → 정보 미제공 조건에서 친한 사람 고르면 친분 편향 점수 ↑ (역량 점수 ↓)
FAKE_CANDIDATES = [
    # 친분 ★★★★★ (최고) — 역량 중간 (5~7)
    {"name": "민준", "rel": "1학년 때부터 친한 동기", "closeness": 5, "ability": 6, "skill": "관리"},
    {"name": "예린", "rel": "MT에서 친해진 동기", "closeness": 5, "ability": 5, "skill": "디자인"},
    {"name": "도윤", "rel": "룸메이트, 매일 같이 공부", "closeness": 5, "ability": 7, "skill": "리서치"},

    # 친분 ★★★★ — 역량 중간~약간 높음 (6~8)
    {"name": "서연", "rel": "친한 친구의 룸메이트", "closeness": 4, "ability": 7, "skill": "발표"},
    {"name": "수아", "rel": "스터디 그룹 멤버", "closeness": 4, "ability": 6, "skill": "통계"},
    {"name": "유진", "rel": "프로젝트 같이 한 신뢰감", "closeness": 4, "ability": 8, "skill": "코딩"},

    # 친분 ★★★ — 역량 다양 (5~9)
    {"name": "James", "rel": "수업 같이 듣는 교환학생", "closeness": 3, "ability": 9, "skill": "AI"},
    {"name": "지호", "rel": "얼굴만 아는 같은 과", "closeness": 3, "ability": 8, "skill": "통계"},
    {"name": "Sarah", "rel": "학회 활동 같이 한 외국인", "closeness": 3, "ability": 9, "skill": "리서치"},

    # 친분 ★★ — 역량 높음 (8~10)
    {"name": "Michael", "rel": "공모전 1번 같이 한", "closeness": 2, "ability": 10, "skill": "코딩"},
    {"name": "현우 선배", "rel": "조교 경험 있는 4학년", "closeness": 2, "ability": 10, "skill": "관리"},
    {"name": "Emma", "rel": "동아리 부원 영어 잘함", "closeness": 2, "ability": 9, "skill": "발표"},

    # 친분 ★ (낮음) — 역량 최고 (9~10)
    {"name": "Daniel", "rel": "이름만 들어본 능력자", "closeness": 1, "ability": 10, "skill": "AI"},
    {"name": "Olivia", "rel": "타과지만 실력 좋은", "closeness": 1, "ability": 10, "skill": "디자인"},
    {"name": "태민", "rel": "한 번 본 적 있는", "closeness": 1, "ability": 9, "skill": "AI"},
]


def save_to_sheets(record: dict) -> bool:
    """Google Sheets에 한 행 추가. st.secrets 가 있으면 사용, 없으면 False."""
    try:
        if "gcp_service_account" not in st.secrets or "sheet_id" not in st.secrets:
            return False
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=scopes
        )
        client = gspread.authorize(creds)
        sh = client.open_by_key(st.secrets["sheet_id"])
        ws = sh.sheet1

        # 헤더 자동 보장
        existing = ws.row_values(1)
        if not existing:
            ws.append_row(list(record.keys()))
            existing = list(record.keys())

        # 누락된 컬럼 합치기
        new_keys = [k for k in record.keys() if k not in existing]
        if new_keys:
            existing = existing + new_keys
            ws.update("A1", [existing])

        row = [str(record.get(k, "")) for k in existing]
        ws.append_row(row)
        return True
    except Exception as e:
        st.toast(f"Sheets 저장 실패: {e}", icon="⚠️")
        return False


def save_to_csv(record: dict) -> None:
    df_new = pd.DataFrame([record])
    if DATA_FILE.exists():
        df_old = pd.read_csv(DATA_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(DATA_FILE, index=False)


def save_response(record: dict) -> None:
    """Sheets 우선, 실패 시 CSV 백업"""
    if not save_to_sheets(record):
        save_to_csv(record)


# ─────────────────────────────────────────────────
# 상태 초기화
# ─────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.frame = random.choice(["gain", "loss"])
    st.session_state.n_cand = random.choice([3, 7, 15])
    st.session_state.info_provided = random.choice([True, False])
    st.session_state.scores = {"L": 0, "G": 0, "P": 0, "R": 0, "D": 0, "C": 0, "I": 0, "A": 0}


def add_score(letter: str, weight: int = 1):
    st.session_state.scores[letter] += weight


def next_step():
    st.session_state.step += 1
    st.rerun()


def prev_step():
    if st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()


def nav_buttons(show_prev: bool = True, next_label: str = "다음 →", on_next=None):
    """이전/다음 버튼 한 쌍. on_next는 callable (저장 등 처리 후 next_step 호출)"""
    if show_prev:
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("← 이전", use_container_width=True):
                prev_step()
        with c2:
            if st.button(next_label, type="primary", use_container_width=True):
                if on_next:
                    on_next()
                else:
                    next_step()
    else:
        if st.button(next_label, type="primary", use_container_width=True):
            if on_next:
                on_next()
            else:
                next_step()


def render_type_grid(highlight: str | None = None) -> str:
    """16가지 유형 4x4 카드 그리드 — 한 줄 HTML로 압축 (Streamlit markdown 호환)"""
    cards = []
    for code, p in TYPES.items():
        is_hl = highlight == code
        border = f"border:3px solid {p['color']};box-shadow:0 0 12px {p['color']}aa" if is_hl else "border:1px solid #e9ecef"
        bg = f"linear-gradient(135deg,{p['color']}22 0%,{p['color']}44 100%)"
        cards.append(
            f'<div style="background:{bg};{border};border-radius:10px;padding:10px 6px;text-align:center">'
            f'<div style="font-size:1.8em;line-height:1.2">{p["emoji"]}</div>'
            f'<div style="font-size:0.85em;font-weight:700;color:{p["color"]};margin-top:2px">{code}</div>'
            f'<div style="font-size:0.7em;color:#495057;line-height:1.2;margin-top:2px">{p["name"]}</div>'
            f'</div>'
        )
    return '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">' + ''.join(cards) + '</div>'


# Admin 모드 — ?admin=lshpy2026 URL 파라미터 시 응답 CSV 다운로드
ADMIN_KEY = "lshpy2026"
qparams = st.query_params
if qparams.get("admin") == ADMIN_KEY:
    st.title("🔐 Admin · 응답 데이터")
    if DATA_FILE.exists():
        df_admin = pd.read_csv(DATA_FILE)
        st.success(f"누적 응답 **{len(df_admin)}**건")
        st.dataframe(df_admin, use_container_width=True)
        with open(DATA_FILE, "rb") as f:
            st.download_button(
                "📥 CSV 다운로드",
                data=f,
                file_name=f"streamlit_responses_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.info("아직 응답 없음.")
    st.stop()


# Debug 모드 — ?debug=lshpy2026 URL 파라미터 시 Sheets 연결 진단
if qparams.get("debug") == ADMIN_KEY:
    st.title("🔧 Debug · Sheets 연결 진단")

    # 1. Secrets 로드 확인
    st.subheader("1️⃣ Secrets 파일 로드 확인")
    try:
        sheet_id = st.secrets.get("sheet_id", None)
        gcp = st.secrets.get("gcp_service_account", None)
        if sheet_id and gcp:
            st.success(f"✅ Secrets 로드됨")
            st.code(f"sheet_id: {sheet_id}\nclient_email: {gcp.get('client_email', '?')}", language="text")
        else:
            st.error("❌ secrets.toml 의 sheet_id 또는 gcp_service_account 가 없음")
            st.stop()
    except Exception as e:
        st.error(f"❌ Secrets 로드 실패: {e}")
        st.stop()

    # 2. 인증
    st.subheader("2️⃣ Google 인증")
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(dict(gcp), scopes=scopes)
        client = gspread.authorize(creds)
        st.success("✅ 인증 성공")
    except Exception as e:
        st.error(f"❌ 인증 실패: {type(e).__name__}: {e}")
        st.info("→ private_key 형식 문제 가능성 (줄바꿈 \\n 살아있는지 확인)")
        st.stop()

    # 3. Sheet 열기
    st.subheader("3️⃣ Sheet 접근")
    try:
        sh = client.open_by_key(sheet_id)
        st.success(f"✅ Sheet 열기 성공: **{sh.title}**")
    except Exception as e:
        st.error(f"❌ Sheet 열기 실패: {type(e).__name__}: {e}")
        st.info("→ Sheet 공유에 서비스 계정 이메일 추가했는지 / Sheet ID 정확한지 확인")
        st.info(f"→ Sheets API + Drive API가 활성화됐는지 확인: https://console.cloud.google.com/apis/library?project={gcp.get('project_id', '')}")
        st.stop()

    # 4. 쓰기 테스트
    st.subheader("4️⃣ 쓰기 테스트")
    try:
        ws = sh.sheet1
        ws.append_row(["debug_test", datetime.now().isoformat(), "성공"])
        st.success("✅ 쓰기 테스트 성공! Sheet 가서 새 행 확인하세요.")
    except Exception as e:
        st.error(f"❌ 쓰기 실패: {type(e).__name__}: {e}")

    # 5. Sheet 정식 초기화
    st.subheader("5️⃣ Sheet 정식 초기화")
    st.caption("응답 컬럼 헤더 + 분석 탭 자동 생성 (1회만 실행)")
    if st.button("🛠️ 시트 초기화 실행", type="primary"):
        try:
            # 응답 탭 (sheet1) 헤더 설정
            HEADERS = [
                "timestamp", "nickname", "grade",
                "attend_A", "attend_B", "attend_C", "attend_check",
                "frame", "leader_intent", "deduct_intent",
                "n_candidates", "info_provided", "decision_style",
                "picked_names", "avg_closeness", "avg_ability",
                "friendship_bias", "ability_score", "decision_time_sec",
                "team_sat", "team_redo",
                "single_w8", "single_w15", "biweek_w8", "biweek_w15", "eval_pref",
                "overall", "influence", "free", "scores",
            ]
            ws = sh.sheet1
            # 기존 데이터 백업 후 클리어
            existing_values = ws.get_all_values()
            ws.clear()
            ws.update_title("응답")
            ws.append_row(HEADERS)
            # 헤더 굵게
            ws.format("A1:AD1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.95, "blue": 1.0}})
            ws.freeze(rows=1)

            # 기존 응답이 있었으면 다시 추가 시도 (헤더 매칭)
            restored = 0
            if len(existing_values) > 1:
                old_headers = existing_values[0]
                for row in existing_values[1:]:
                    rec = dict(zip(old_headers, row))
                    new_row = [rec.get(h, "") for h in HEADERS]
                    ws.append_row(new_row)
                    restored += 1

            # 분석 탭 추가
            try:
                analysis = sh.add_worksheet(title="분석", rows=50, cols=10)
            except Exception:
                analysis = sh.worksheet("분석")

            analysis_rows = [
                ["IMEN315 학습 MBTI 응답 실시간 대시보드", "", "", ""],
                ["", "", "", ""],
                ["📊 응답자 수", "=COUNTA(응답!A2:A)", "", ""],
                ["", "", "", ""],
                ["🧬 16 유형 분포", "", "", ""],
                ["코드", "이름", "응답 수", "비율"],
                ["LPDA", "안정의 분석가", '=COUNTIF(응답!AD:AD,"*\'L\': "*"\'P\': "*"\'D\': "*"\'A\': "*")', "=C7/$B$3"],
                ["", "", "", ""],
                ["🛡️ vs 🚀 동기 차원", "", "", ""],
                ["손실 회피 (L) > 이득 추구 (G)", '=COUNTIF(응답:응답!AD2:AD,"*L\': 2*")', "", ""],
                ["", "", "", ""],
                ["⏱️ 평균 결정 시간 (팀 구성)", "=AVERAGE(응답!S2:S)", "초", ""],
                ["", "", "", ""],
                ["🤝 친분 편향 평균", "=AVERAGE(응답!Q2:Q)", "(0~1)", ""],
                ["📈 역량 점수 평균", "=AVERAGE(응답!R2:R)", "(0~1)", ""],
                ["", "", "", ""],
                ["📅 시간별 응답 (최근)", "", "", ""],
                ["timestamp", "닉네임", "유형", "결정시간"],
            ]
            analysis.clear()
            for r in analysis_rows:
                analysis.append_row(r)
            analysis.format("A1", {"textFormat": {"bold": True, "fontSize": 14}})
            analysis.format("A3:A18", {"textFormat": {"bold": True}})

            st.success(f"✅ 초기화 완료! 응답 탭 헤더 {len(HEADERS)}개 + 분석 탭 생성. 기존 응답 {restored}개 복원.")
            st.balloons()
            st.markdown(f"[📊 시트 열기]({sh.url})")
        except Exception as e:
            st.error(f"❌ 초기화 실패: {type(e).__name__}: {e}")

    st.stop()


# 진행률
TOTAL = 7
if 0 < st.session_state.step < TOTAL:
    st.progress(st.session_state.step / (TOTAL - 1))
    st.caption(f"📖 챕터 {st.session_state.step} / {TOTAL - 1}")


# ─────────────────────────────────────────────────
# 챕터 0: 인트로 + 16 유형 미리보기
# ─────────────────────────────────────────────────
def page_intro():
    st.markdown(
        """
        <div style="text-align:center;padding:24px 0">
            <div style="font-size:3.5em;line-height:1">🧬</div>
            <div style="font-size:2em;font-weight:800;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
                학습 MBTI
            </div>
            <div style="color:#868e96;margin-top:4px">IMEN315 인간공학 강의계획서 인식 조사</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 16가지 학습 유형 — 당신은 어디에?")
    import streamlit.components.v1 as components
    components.html(render_type_grid(), height=500, scrolling=False)

    st.markdown("&nbsp;")
    st.markdown(
        """
        ### 🎯 4가지 차원으로 분석

        - 🛡️ **L** 손실 회피 vs 🚀 **G** 이득 추구
        - 📐 **P** 예측 가능 vs 🎲 **R** 무작위 적응
        - 📚 **D** 분산 학습 vs 🔥 **C** 집중 학습
        - 💭 **I** 직관 결정 vs 🔍 **A** 분석 결정

        ⏱️ 약 5분 · 🔒 익명 · 📊 6/12 보고서에 익명 통계로만 반영
        """
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.session_state.answers["nickname"] = st.text_input("🧑 익명 닉네임", "익명의 수강생", max_chars=20)
    with col2:
        st.session_state.answers["grade"] = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "기타"])

    nav_buttons(show_prev=False, next_label="🧬 시작하기 →")


# ─────────────────────────────────────────────────
# 챕터 1: 출석
# ─────────────────────────────────────────────────
def page_attendance():
    st.title("📅 챕터 1 — 출석 정책")
    st.info("**상황**: 비 오는 화요일 아침. 같은 비 오는 날인데 수업 출석 정책이 3가지로 다릅니다.")

    st.markdown("### 🌧️ A — *매주 월요일에만 체크*")
    a = st.select_slider("이 정책에서 비 오는 화요일에 갈 의향?",
                          ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"],
                          value="🤔 모름", key="att_a")
    st.markdown("### 🎲 B — *30회 중 7회 무작위 (횟수만 알려줌)*")
    b = st.select_slider("갈 의향?",
                          ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"],
                          value="🤔 모름", key="att_b")
    st.markdown("### 🌫️ C — *완전 무작위 (횟수도 비공개)*")
    c = st.select_slider("갈 의향?",
                          ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"],
                          value="🤔 모름", key="att_c")

    st.markdown("---")
    check = st.radio("🔍 **이해 확인** — 위 셋 중 가장 예측 불가능한 정책은?",
                     ["A", "B", "C"], index=2, horizontal=True)

    def _save():
        m = {"😴 절대 안 감": 1, "😪 별로": 2, "🤔 모름": 3, "🙂 갈까": 4, "🏃 갈래": 5}
        st.session_state.answers.update(attend_A=m[a], attend_B=m[b], attend_C=m[c], attend_check=check)
        if m[a] >= m[c]:
            add_score("P", 2)
        else:
            add_score("R", 2)
        next_step()
    nav_buttons(on_next=_save)


# ─────────────────────────────────────────────────
# 챕터 2: 팀장 인센티브
# ─────────────────────────────────────────────────
def page_framing():
    st.title("👑 챕터 2 — 팀장 정책")
    st.markdown("**상황**: 1주차 끝. 교수님이 팀장 자원자를 모집합니다.")

    st.caption("(가상 비교 실험 — 같은 ±10점 차이를 두 표현으로 보여주고 반응 차이 측정)")
    if st.session_state.frame == "gain":
        st.success("📢 **교수님 [표현 A]**: \"팀장에 자원하면 **+10점 가산**해드립니다!\"")
    else:
        st.error("📢 **교수님 [표현 B]**: \"기본 점수에서 출발하지만 팀장 책임을 미이행하면 **-10점 차감**됩니다.\"")

    intent = st.radio("🤚 자원하시겠습니까?",
                       ["💯 적극 자원", "😊 의향 있음", "🤔 고민", "😐 별로", "🙅 절대 안 함"], index=2)
    deduct = st.select_slider("💢 팀원이 무임승차하면 감점 발의?",
                               ["전혀", "잘 안 함", "보통", "할듯", "당연히"], value="보통")

    def _save():
        m_intent = {"💯 적극 자원": 7, "😊 의향 있음": 5, "🤔 고민": 4, "😐 별로": 2, "🙅 절대 안 함": 1}
        m_deduct = {"전혀": 1, "잘 안 함": 3, "보통": 4, "할듯": 5, "당연히": 7}
        st.session_state.answers.update(
            frame=st.session_state.frame, leader_intent=m_intent[intent], deduct_intent=m_deduct[deduct])
        if st.session_state.frame == "loss" and m_intent[intent] >= 5:
            add_score("L", 2)
        elif st.session_state.frame == "gain" and m_intent[intent] >= 5:
            add_score("G", 2)
        elif st.session_state.frame == "loss" and m_intent[intent] <= 3:
            add_score("G", 1)
        else:
            add_score("L", 1)
        next_step()
    nav_buttons(on_next=_save)


# ─────────────────────────────────────────────────
# 챕터 3: 팀 구성 (가상 이름)
# ─────────────────────────────────────────────────
def page_team():
    st.title("👥 챕터 3 — 팀원 2명 직접 지명")
    n = st.session_state.n_cand
    info = st.session_state.info_provided

    if "team_start_time" not in st.session_state:
        st.session_state.team_start_time = datetime.now()

    st.markdown(
        f"**상황**: 강의계획서대로 **팀장이 직접 지명할 수 있는 인원은 2명**. "
        f"나머지 2명은 자동 배정됩니다.\n\n"
        f"후보 **{n}명** 중 **정확히 2명**을 지명하세요."
    )

    # 후보 풀 무작위 추출 (시드 고정으로 같은 응답자 그룹 내 일관성)
    rng = random.Random(42)
    pool = FAKE_CANDIDATES.copy()
    rng.shuffle(pool)
    cands = pool[:n]

    if info:
        st.success("📋 **프로필 카드 제공** — 이름·관계·역량·관심분야 (정보 충분)")
        # 표 보이기
        df_show = pd.DataFrame([{
            "이름": c["name"],
            "관계": c["rel"],
            "역량(1-10)": c["ability"],
            "관심": c["skill"],
        } for c in cands])
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.warning("❗ **이름·관계만** — 역량 정보 없음 (제한된 정보)")
        cols = st.columns(min(n, 5))
        for i, c in enumerate(cands):
            with cols[i % len(cols)]:
                st.markdown(f"🧑 **{c['name']}**")
                st.caption(c["rel"])

    st.markdown("---")
    st.markdown("### 🎯 2명을 지명하세요 (강의계획서 규칙: 팀장 직접 지명 최대 2명)")

    options = [f"{c['name']} ({c['rel']})" for c in cands]
    picked = st.multiselect(
        "지명할 팀원 2명 (정확히 2명)",
        options,
        max_selections=2,
        placeholder="후보 풀에서 2명 지명",
    )

    if len(picked) != 2:
        st.info(f"현재 {len(picked)}/2명 지명. 정확히 2명 골라주세요.")

    sat = st.select_slider("🎯 본인의 지명에 만족합니까?",
                            ["😩 전혀", "😟 별로", "😐 그저", "🙂 만족", "🤩 매우"], value="😐 그저")
    redo = st.radio("🔁 같은 상황 다시 와도 같은 2명?",
                    ["✅ 예", "❌ 아니오"], horizontal=True)

    def _save():
        if len(picked) != 2:
            st.error("정확히 2명을 지명해주세요!")
            return

        # 선택된 후보 매핑
        picked_names = [p.split(" (")[0] for p in picked]
        picked_cands = [c for c in cands if c["name"] in picked_names]

        # 측정 지표 계산 (2명 기준)
        avg_closeness = sum(c["closeness"] for c in picked_cands) / 2
        avg_ability = sum(c["ability"] for c in picked_cands) / 2
        top2_closeness = sorted([c["closeness"] for c in cands], reverse=True)[:2]
        max_closeness = sum(top2_closeness) / 2
        friendship_bias = avg_closeness / max_closeness if max_closeness > 0 else 0
        top2_ability = sorted([c["ability"] for c in cands], reverse=True)[:2]
        max_ability = sum(top2_ability) / 2
        ability_score = avg_ability / max_ability if max_ability > 0 else 0

        decision_time_sec = (datetime.now() - st.session_state.team_start_time).total_seconds()

        m = {"😩 전혀": 1, "😟 별로": 2, "😐 그저": 4, "🙂 만족": 6, "🤩 매우": 7}
        st.session_state.answers.update(
            n_candidates=n, info_provided=info,
            picked_names=";".join(picked_names),
            avg_closeness=round(avg_closeness, 2),
            avg_ability=round(avg_ability, 2),
            friendship_bias=round(friendship_bias, 3),
            ability_score=round(ability_score, 3),
            decision_time_sec=round(decision_time_sec, 1),
            team_sat=m[sat],
            team_redo=("yes" if "예" in redo else "no"),
        )

        # I vs A 점수: 친분 편향 높으면 I (직관/친분), 역량 점수 높으면 A (분석)
        if friendship_bias > 0.75:
            add_score("I", 2)
        elif ability_score > 0.85:
            add_score("A", 2)
        else:
            add_score("I", 1)
            add_score("A", 1)

        next_step()
    nav_buttons(on_next=_save)


# ─────────────────────────────────────────────────
# 챕터 4: 평가 체계
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

    pref = st.radio("📌 둘 중 어떤 평가가 본인에게 더 잘 맞을 것 같아요?",
                    ["📕 단일 기말 (집중 폭발)", "📗 격주 퀴즈 (꾸준 분산)"], horizontal=True)

    def _save():
        st.session_state.answers.update(
            single_w8=a8, single_w15=a15, biweek_w8=b8, biweek_w15=b15, eval_pref=pref)
        cramming = a15 - a8
        spreading = b15 - b8
        if cramming > spreading + 3 or "단일" in pref:
            add_score("C", 2)
        else:
            add_score("D", 2)
        next_step()
    nav_buttons(on_next=_save)


# ─────────────────────────────────────────────────
# 챕터 5: 마무리
# ─────────────────────────────────────────────────
def page_final():
    st.title("🎬 챕터 5 — 마무리")

    overall = st.slider("🎓 IMEN315 강의계획서 만족도", 1, 7, 4)
    influence = st.slider("✨ 강의계획서가 행동에 영향?", 1, 7, 4)
    free = st.text_area("✍️ 자유 의견 (선택)", height=80)

    def _save():
        st.session_state.answers.update(
            overall=overall, influence=influence, free=free,
            timestamp=datetime.now().isoformat(),
            scores=str(st.session_state.scores))
        try:
            save_response(st.session_state.answers)
        except Exception:
            pass
        next_step()
    nav_buttons(next_label="🧬 결과 보기", on_next=_save)


# ─────────────────────────────────────────────────
# 챕터 6: 결과
# ─────────────────────────────────────────────────
def page_result():
    s = st.session_state.scores

    code = ""
    code += "L" if s["L"] >= s["G"] else "G"
    code += "P" if s["P"] >= s["R"] else "R"
    code += "D" if s["D"] >= s["C"] else "C"
    code += "I" if s["I"] >= s["A"] else "A"

    p = TYPES.get(code, {"emoji": "❓", "name": "분석 중", "desc": "", "color": "#868e96"})

    st.balloons()
    st.markdown(
        f"""
        <div style="text-align:center;background:linear-gradient(135deg,{p["color"]} 0%,{p["color"]}cc 100%);
        color:white;padding:32px 16px;border-radius:16px;margin:8px 0;
        box-shadow:0 8px 24px {p["color"]}55">
        <div style="font-size:0.9em;opacity:0.9">당신의 학습 MBTI</div>
        <div style="font-size:5em;line-height:1.1;margin:8px 0">{p['emoji']}</div>
        <div style="font-size:3.5em;font-weight:900;letter-spacing:0.15em">{code}</div>
        <div style="font-size:1.6em;margin-top:8px;font-weight:600">{p['name']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**해설**: {p['desc']}")

    st.markdown("---")
    st.subheader("📊 4가지 차원 점수")

    for label, l1, l2, name1, name2 in DIMENSIONS:
        v1, v2 = s[l1], s[l2]
        total = v1 + v2 if (v1 + v2) > 0 else 1
        pct1 = round(100 * v1 / total)
        pct2 = 100 - pct1
        cols = st.columns([1, 4, 1])
        with cols[0]:
            st.write(f"**{label}**")
        with cols[1]:
            st.write(f"{l1} ({name1}) **{pct1}%** — **{pct2}%** ({name2}) {l2}")
            st.progress(pct1 / 100)
        with cols[2]:
            winner = l1 if v1 >= v2 else l2
            st.metric("", winner)

    st.markdown("---")
    st.subheader("🧬 16가지 유형 (당신 위치 강조)")
    import streamlit.components.v1 as components
    components.html(render_type_grid(highlight=code), height=500, scrolling=False)

    st.markdown("---")

    a = st.session_state.answers
    if a.get("frame") == "loss" and a.get("leader_intent", 0) >= 5:
        st.info(
            "💡 **흥미로운 발견** — 당신은 '-10점 차감' 시나리오에서 자원 의도가 높았어요. "
            "**Prospect Theory(Tversky & Kahneman)**가 예측한 인류 평균 — "
            "사람은 손실을 이득보다 약 2배 강하게 느낍니다."
        )

    cramming = a.get("single_w15", 0) - a.get("single_w8", 0)
    if cramming > 5:
        st.warning(
            f"⚠️ **벼락치기 패턴 감지** — 단일 기말 시나리오에서 학기말 학습이 {cramming:.0f}h 증가. "
            "**Forgetting Curve(Ebbinghaus)** 가 예측하는 비효율 패턴이에요. "
            "분산 학습이 인출 시간을 약 3.4배 단축한다는 시뮬 결과 있음."
        )

    fb = a.get("friendship_bias", 0)
    abil = a.get("ability_score", 0)
    if fb > 0.75 and not a.get("info_provided"):
        st.warning(
            f"🤝 **친분 휴리스틱 발현** — 정보 미제공 조건에서 친분 편향 점수 **{fb:.0%}**, "
            f"역량 점수 **{abil:.0%}**. **Satisficing(Simon)** 이 작동했어요. "
            "사람 머리는 한 번에 7±2개 정보만 처리 가능 — 정보가 부족하면 친한 사람으로 채움."
        )
    elif abil > 0.9:
        st.success(
            f"📊 **분석 우선** — 역량 점수 **{abil:.0%}**, 친분 편향 **{fb:.0%}**. "
            "친분보다 객관 정보로 결정하는 분석가 타입이에요."
        )

    dt = a.get("decision_time_sec", 0)
    if dt > 0:
        st.caption(f"⏱️ 결정 시간: {dt:.1f}초")

    st.markdown("---")
    st.success("🙇 **응답 감사합니다!** 결과는 6/12 보고서 제출 후 단톡에 익명 요약으로 공유됩니다.")
    st.caption("자세한 이론은 [GitHub](https://github.com/lshpy/imen315-syllabus-meta) 참고")

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
