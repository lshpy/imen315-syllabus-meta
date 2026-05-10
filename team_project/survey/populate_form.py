"""기존 빈 Google Form에 22개 문항을 일괄 추가."""
from __future__ import annotations
import sys
from pathlib import Path
import toml
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

FORM_ID = sys.argv[1] if len(sys.argv) > 1 else "19z8xwozNmpfDXNiI5wvIpSCYhjj8I5wnyTDYcnRAq3M"

SECRETS = toml.load(".streamlit/secrets.toml")
SCOPES = ["https://www.googleapis.com/auth/forms.body"]
creds = Credentials.from_service_account_info(SECRETS["gcp_service_account"], scopes=SCOPES)
forms = build("forms", "v1", credentials=creds)

SCALE_5 = ["😴 절대 안 감", "😪 별로", "🤔 모름", "🙂 갈까", "🏃 갈래"]
INTENT_5 = ["💯 적극 자원", "😊 의향 있음", "🤔 고민", "😐 별로", "🙅 절대 안 함"]
DEDUCT_5 = ["전혀", "잘 안 함", "보통", "할듯", "당연히"]
SAT_5 = ["😩 전혀", "😟 별로", "😐 그저", "🙂 만족", "🤩 매우"]


def section(title, description=""):
    return {"item": {"title": title, "description": description, "pageBreakItem": {}}}


def choice(title, options, required=True):
    return {"item": {"title": title, "questionItem": {"question": {
        "required": required,
        "choiceQuestion": {"type": "RADIO", "options": [{"value": o} for o in options]},
    }}}}


def scale(title, low=1, high=7, low_label="전혀", high_label="매우"):
    return {"item": {"title": title, "questionItem": {"question": {
        "required": True,
        "scaleQuestion": {"low": low, "high": high, "lowLabel": low_label, "highLabel": high_label},
    }}}}


def text_q(title, paragraph=False, required=False):
    return {"item": {"title": title, "questionItem": {"question": {
        "required": required,
        "textQuestion": {"paragraph": paragraph},
    }}}}


items = [
    choice("Q1. 학년", ["1학년", "2학년", "3학년", "4학년", "졸업유예·기타"]),
    text_q("Q2. 소속 학과 (예: 산업경영공학부)", required=True),
    choice("Q3. 직전 학기 학점", ["4.0 이상", "3.5–4.0", "3.0–3.5", "3.0 미만", "응답 안 함"]),
    choice("Q4. 평소 출석률", ["95% 이상", "80–95%", "60–80%", "60% 미만"]),
    section("📅 출석 정책 시나리오", "비 오는 화요일 아침. 같은 비 오는 날인데 정책이 3가지로 다릅니다."),
    choice("Q5. A — 매주 월요일에만 출석 체크. 결석할 의도?", SCALE_5),
    choice("Q6. B — 30회 중 7회 무작위 (횟수만 알려줌). 결석할 의도?", SCALE_5),
    choice("Q7. C — 무작위 + 횟수 비공개. 결석할 의도?", SCALE_5),
    choice("Q8. [이해 확인] 가장 예측 불가능한 정책은?", ["A", "B", "C"]),
    section("👑 팀장 인센티브"),
    choice("Q9. 두 메시지 중 어느 것을 본 상황으로 가정 (가상 비교 실험)",
           ["A. '팀장 자원자에게 +10점 가산'",
            "B. '기본 점수에서 팀장 책임 미이행 시 -10점 차감'"]),
    choice("Q10. 팀장에 자원할 의도?", INTENT_5),
    choice("Q11. 팀원 무임승차 시 감점 발의 의도?", DEDUCT_5),
    section("👥 팀원 직접 지명 (강의계획서 규칙: 팀장이 최대 2명 직접 지명)",
            "후보 7명: 민준(친한 동기), James(교환학생, 능력 우수), 예린(친한 친구), Sarah(외국인 학회 동료), Michael(공모전 본 적 있는 능력자), 도윤(룸메이트), Daniel(이름만 들어본 능력자). 이 중 2명을 지명하세요."),
    choice("Q12. 어떻게 결정하시겠어요?",
           ["💭 직감으로 빠르게", "🔍 정보 다 비교 후 신중히", "🤝 친한 사람부터", "📊 점수 매겨서 상위 2명"]),
    choice("Q13. 본인이 지명한 2명에 만족?", SAT_5),
    choice("Q14. 같은 상황 다시 와도 같은 2명?", ["✅ 예", "❌ 아니오"]),
    section("📚 평가 체계와 학습시간"),
    text_q("Q15. [단일 기말 40%] 8주차 학습/주 (시간, 숫자만)", required=True),
    text_q("Q16. [단일 기말 40%] 15주차 학습/주", required=True),
    text_q("Q17. [격주 퀴즈 6회 + 기말] 8주차 학습/주", required=True),
    text_q("Q18. [격주 퀴즈 6회 + 기말] 15주차 학습/주", required=True),
    choice("Q19. 둘 중 본인에게 더 잘 맞을 평가?",
           ["📕 단일 기말 (집중 폭발)", "📗 격주 퀴즈 (꾸준 분산)"]),
    section("🎬 마무리"),
    scale("Q20. IMEN315 강의계획서 만족도", 1, 7, "매우 불만", "매우 만족"),
    scale("Q21. 강의계획서가 행동에 영향?", 1, 7, "전혀", "매우"),
    text_q("Q22. (선택) 자유 의견", paragraph=True, required=False),
    text_q("Q23. (선택) 닉네임", required=False),
]

requests = []
# 폼 정보 업데이트
requests.append({
    "updateFormInfo": {
        "info": {
            "title": "IMEN315 학습 MBTI - Google Forms 대조군",
            "description": (
                "IMEN315 인간공학 팀프로젝트 설문.\n"
                "약 5분 소요 · 모든 답변 익명 · 보고서에 통계로만 반영.\n\n"
                "🧬 게임형 버전: https://imen315-syllabus-meta-gpvxmznvcygwd9cln2bnjp.streamlit.app/"
            ),
        },
        "updateMask": "title,description",
    }
})
# 항목 추가
for i, it in enumerate(items):
    requests.append({"createItem": {"item": it["item"], "location": {"index": i}}})

result = forms.forms().batchUpdate(formId=FORM_ID, body={"requests": requests}).execute()
form = forms.forms().get(formId=FORM_ID).execute()

view_url = form.get("responderUri", f"https://docs.google.com/forms/d/{FORM_ID}/viewform")
edit_url = f"https://docs.google.com/forms/d/{FORM_ID}/edit"

out = Path(__file__).parent / "form_url.txt"
out.write_text(f"FORM_ID: {FORM_ID}\nEDIT: {edit_url}\nFILL: {view_url}\n", encoding="utf-8")

print(f"✅ {len(items)}개 항목 추가 완료")
print(f"\n📋 응답용 (배포):  {view_url}")
print(f"📝 편집용:        {edit_url}")
