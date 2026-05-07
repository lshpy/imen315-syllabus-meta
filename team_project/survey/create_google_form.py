"""Google Forms 자동 생성 스크립트 (B. 대조군 백업).

전제:
    1. Google Forms API 활성화 — https://console.cloud.google.com/apis/library/forms.googleapis.com?project=imen315-survey
    2. 같은 서비스 계정 (.streamlit/secrets.toml) 사용

실행:
    python team_project/survey/create_google_form.py

산출:
    team_project/survey/form_url.txt — 생성된 Form URL 저장
"""
from __future__ import annotations

from pathlib import Path
import toml
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SECRETS = toml.load(".streamlit/secrets.toml")
SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
]
creds = Credentials.from_service_account_info(SECRETS["gcp_service_account"], scopes=SCOPES)
forms_service = build("forms", "v1", credentials=creds)


# ─────────────────────────────────────────────────
# 1. 빈 폼 생성
# ─────────────────────────────────────────────────
form = forms_service.forms().create(body={
    "info": {"title": "IMEN315 학습 MBTI - Google Forms 대조군"}
}).execute()

FORM_ID = form["formId"]
print(f"✅ 폼 생성: {FORM_ID}")
print(f"   편집: {form['responderUri'].replace('/viewform', '/edit')}")
print(f"   응답: {form['responderUri']}")


# ─────────────────────────────────────────────────
# 2. 설명 + 문항 일괄 추가 (batchUpdate)
# ─────────────────────────────────────────────────
SCALE_5 = ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"]
INTENT_5 = ["💯 적극 자원", "😊 의향 있음", "🤔 고민", "😐 별로", "🙅 절대 안 함"]
DEDUCT_5 = ["전혀", "잘 안 함", "보통", "할듯", "당연히"]
SAT_5 = ["😩 전혀", "😟 별로", "😐 그저", "🙂 만족", "🤩 매우"]


def section(title: str, description: str = ""):
    return {"createItem": {"item": {
        "title": title,
        "description": description,
        "pageBreakItem": {},
    }, "location": {"index": "PLACEHOLDER"}}}


def choice(title: str, options: list[str], required: bool = True, image: str = None):
    return {"createItem": {"item": {
        "title": title,
        "questionItem": {"question": {
            "required": required,
            "choiceQuestion": {
                "type": "RADIO",
                "options": [{"value": o} for o in options],
            },
        }},
    }, "location": {"index": "PLACEHOLDER"}}}


def scale(title: str, low: int = 1, high: int = 7, low_label: str = "전혀", high_label: str = "매우"):
    return {"createItem": {"item": {
        "title": title,
        "questionItem": {"question": {
            "required": True,
            "scaleQuestion": {
                "low": low, "high": high,
                "lowLabel": low_label, "highLabel": high_label,
            },
        }},
    }, "location": {"index": "PLACEHOLDER"}}}


def text(title: str, paragraph: bool = False, required: bool = False):
    return {"createItem": {"item": {
        "title": title,
        "questionItem": {"question": {
            "required": required,
            "textQuestion": {"paragraph": paragraph},
        }},
    }, "location": {"index": "PLACEHOLDER"}}}


def number(title: str):
    return {"createItem": {"item": {
        "title": title,
        "questionItem": {"question": {
            "required": True,
            "textQuestion": {"paragraph": False},
        }},
    }, "location": {"index": "PLACEHOLDER"}}}


# 폼 항목 정의 (순서 중요)
items = [
    # 인구통계
    choice("Q1. 학년", ["1학년", "2학년", "3학년", "4학년", "졸업유예·기타"]),
    text("Q2. 소속 학과 (예: 산업경영공학부)", required=True),
    choice("Q3. 직전 학기 학점", ["4.0 이상", "3.5–4.0", "3.0–3.5", "3.0 미만", "응답 안 함"]),
    choice("Q4. 평소 출석률", ["95% 이상", "80–95%", "60–80%", "60% 미만"]),

    # 출석 시나리오 (within-subjects)
    section("📅 출석 정책 시나리오",
            "비 오는 화요일 아침. 같은 비 오는 날인데 수업 출석 정책이 3가지로 다릅니다."),
    choice("Q5. 시나리오 A — 매주 월요일에만 출석 체크. 결석할 의도?", SCALE_5),
    choice("Q6. 시나리오 B — 30회 중 7회 무작위(횟수만 알려줌). 결석할 의도?", SCALE_5),
    choice("Q7. 시나리오 C — 무작위 + 횟수 비공개. 결석할 의도?", SCALE_5),
    choice("Q8. [이해 확인] 위 셋 중 가장 예측 불가능한 정책은?", ["A", "B", "C"]),

    # Framing
    section("👑 팀장 인센티브 시나리오",
            "교수님이 팀장 자원자를 모집합니다."),
    choice("Q9. 어느 메시지를 보았다고 가정하시겠어요? (무작위 분기 대신 선택)",
           ["A. 팀장 자원자에게 +10점 가산",
            "B. 팀장 안 맡으면 -10점 차감"]),
    choice("Q10. 위 정책에서 팀장에 자원할 의도?", INTENT_5),
    choice("Q11. 팀원 무임승차 시 감점 발의 의도?", DEDUCT_5),

    # 팀 구성
    section("👥 5명 팀 구성",
            "후보 7명: 민준(친한 동기), James(교환학생, 능력 우수), 예린(친한 친구), Sarah(외국인 학회 동료), Michael(공모전 본 적 있는 능력자), 도윤(룸메이트), Daniel(이름만 들어본 능력자). 5명을 골라야 합니다."),
    choice("Q12. 어떻게 결정하시겠어요?",
           ["💭 직감으로 빠르게",
            "🔍 정보 다 비교 후 신중히",
            "🤝 친한 사람부터",
            "📊 점수 매겨서 상위 5명"]),
    choice("Q13. 본인이 고른 5명에 만족하시겠어요?", SAT_5),
    choice("Q14. 같은 상황 다시 와도 같은 5명?", ["✅ 예", "❌ 아니오"]),

    # 평가 체계
    section("📚 평가 체계와 학습시간",
            "두 평가 시스템에서 본인 학습 패턴 예상."),
    text("Q15. [단일 기말 40%] 8주차 학습시간/주 (시간, 숫자만)", required=True),
    text("Q16. [단일 기말 40%] 15주차 학습시간/주 (시간, 숫자만)", required=True),
    text("Q17. [격주 퀴즈 6회 + 기말 40%] 8주차 학습시간/주", required=True),
    text("Q18. [격주 퀴즈 6회 + 기말 40%] 15주차 학습시간/주", required=True),
    choice("Q19. 둘 중 본인에게 더 잘 맞을 평가?",
           ["📕 단일 기말 (집중 폭발)", "📗 격주 퀴즈 (꾸준 분산)"]),

    # 마무리
    section("🎬 마무리"),
    scale("Q20. IMEN315 강의계획서 만족도", 1, 7, "매우 불만", "매우 만족"),
    scale("Q21. 강의계획서가 행동에 영향?", 1, 7, "전혀", "매우"),
    text("Q22. (선택) 자유 의견", paragraph=True, required=False),
    text("Q23. (선택) 닉네임", required=False),
]

# index 부여
requests = []
for i, item in enumerate(items):
    item_copy = {**item}
    item_copy["createItem"]["location"] = {"index": i}
    requests.append(item_copy)

# 일괄 추가
forms_service.forms().batchUpdate(formId=FORM_ID, body={"requests": requests}).execute()
print(f"✅ {len(items)}개 항목 추가 완료")


# ─────────────────────────────────────────────────
# 3. 폼 설명 업데이트
# ─────────────────────────────────────────────────
forms_service.forms().batchUpdate(formId=FORM_ID, body={"requests": [{
    "updateFormInfo": {
        "info": {
            "description": (
                "IMEN315 인간공학 팀프로젝트 설문 (Google Forms · 대조군 B).\n"
                "약 5분 소요. 모든 답변은 익명, 보고서에 통계로만 반영.\n\n"
                "🧬 Streamlit 게임형 버전: https://imen315-syllabus-meta-gpvxmznvcygwd9cln2bnjp.streamlit.app/"
            ),
        },
        "updateMask": "description",
    },
}]}).execute()


# ─────────────────────────────────────────────────
# 4. URL 저장
# ─────────────────────────────────────────────────
out_path = Path(__file__).parent / "form_url.txt"
edit_url = f"https://docs.google.com/forms/d/{FORM_ID}/edit"
view_url = form["responderUri"]
out_path.write_text(f"FORM_ID: {FORM_ID}\nEDIT: {edit_url}\nFILL: {view_url}\n", encoding="utf-8")

print(f"\n📋 응답용 URL (단톡 배포):")
print(f"   {view_url}")
print(f"\n📝 편집 URL:")
print(f"   {edit_url}")
print(f"\n→ {out_path} 에 저장됨")
