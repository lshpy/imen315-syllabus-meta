# Google Sheets 연동 가이드

응답 데이터를 실시간으로 Google Sheets에 저장하는 1회 세팅 가이드.

세팅 후 Streamlit Cloud + 로컬 모두에서 같은 Sheet에 응답이 누적됩니다.

---

## 🛠️ 1단계: Google Sheet 만들기

1. https://sheets.google.com 에서 새 스프레드시트 만들기
2. 이름: `IMEN315 학습MBTI 응답` (자유)
3. 시트 URL 복사:
   ```
   https://docs.google.com/spreadsheets/d/【SHEET_ID】/edit
   ```
   `【SHEET_ID】` 부분이 Sheet ID — 메모

---

## 🔑 2단계: 서비스 계정 만들기 (GCP)

1. https://console.cloud.google.com 접속 → 새 프로젝트 만들기 (이름 자유, 예: `imen315-survey`)

2. **API 활성화**:
   - "API 및 서비스" → "라이브러리"
   - **Google Sheets API** 검색 → 사용 설정
   - **Google Drive API** 검색 → 사용 설정

3. **서비스 계정 생성**:
   - "API 및 서비스" → "사용자 인증 정보"
   - **사용자 인증 정보 만들기** → **서비스 계정**
   - 이름: `streamlit-survey` (자유) → 만들기 → 완료

4. **JSON 키 다운로드**:
   - 만든 서비스 계정 클릭 → **키** 탭 → **키 추가** → **새 키 만들기**
   - 유형: **JSON** → 만들기 → 자동으로 .json 다운로드됨
   - **이 JSON 파일은 비밀번호처럼 다루세요!** GitHub에 절대 올리지 마세요.

5. 다운로드된 JSON 안에서 `client_email` 필드 값 복사 (예: `streamlit-survey@imen315-survey.iam.gserviceaccount.com`)

---

## 🤝 3단계: Sheet에 서비스 계정 권한 부여

1. 1단계에서 만든 Google Sheet 열기
2. 우측 상단 **공유** 클릭
3. 위에서 복사한 **서비스 계정 이메일** 추가 → **편집자** 권한
4. **링크 복사** → 보내기

---

## ☁️ 4단계: Streamlit Cloud Secrets 입력

1. https://share.streamlit.io 에서 본인 앱 대시보드
2. 앱 우측 점 3개 → **Settings** → **Secrets**
3. 아래 양식 그대로 입력 (TOML 형식):

```toml
sheet_id = "여기에_1단계_Sheet_ID_붙여넣기"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "streamlit-survey@...iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

> 위 값들은 모두 **2단계에서 다운받은 JSON 파일** 안에 있어요. 그대로 복사 → 붙여넣기.
> `private_key`는 줄바꿈(`\n`) 그대로 유지.

4. **Save** → 앱 자동 재시작

---

## 💻 5단계 (선택): 로컬에서도 같은 Sheet 사용

`.streamlit/secrets.toml` 파일 만들기:

```bash
mkdir -p ~/.streamlit
cat > ~/.streamlit/secrets.toml << 'EOF'
sheet_id = "..."

[gcp_service_account]
... (위와 동일)
EOF
```

또는 프로젝트 루트에 `.streamlit/secrets.toml` (이건 `.gitignore` 처리 자동됨).

---

## ✅ 확인

앱 실행 → 설문 한 번 끝 → Google Sheet 새로고침 → 응답 한 행 보이면 성공!

응답 안 들어오면:
- 서비스 계정에 Sheet 편집자 권한 줬는지
- Sheets API · Drive API 활성화됐는지
- Secrets 입력 시 `private_key`의 `\n` 살아있는지

---

## 📊 데이터 분석

```bash
# 로컬에서 Sheet 다운로드해서 분석
python -c "
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

creds = Credentials.from_service_account_file('keys/service_account.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets'])
client = gspread.authorize(creds)
sh = client.open_by_key('YOUR_SHEET_ID')
df = pd.DataFrame(sh.sheet1.get_all_records())
df.to_csv('responses.csv', index=False)
print(f'다운로드 완료: {len(df)} 응답')
"
```

또는 Sheet에서 **파일 → 다운로드 → CSV** 한 번에 가능.
