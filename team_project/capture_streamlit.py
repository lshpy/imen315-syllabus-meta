"""Streamlit 앱 스크린샷 캡처"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path(__file__).parent / "screenshots"
OUT.mkdir(exist_ok=True)


async def click_by_text(page, text, fallback_role="button"):
    try:
        await page.get_by_role(fallback_role, name=text).first.click(timeout=3000)
        await page.wait_for_timeout(1500)
    except Exception as e:
        print(f"  click fail: {text} — {e}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1280, "height": 1600})
        page = await ctx.new_page()
        await page.goto("http://localhost:8501", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(2000)

        # 1) 인트로
        await page.screenshot(path=str(OUT / "01_intro.png"), full_page=True)
        print("✅ 01 intro")

        # 시작 버튼
        await click_by_text(page, "시작하기")

        # 2) 출석 챕터
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / "02_attendance.png"), full_page=True)
        print("✅ 02 attendance")

        # 다음
        await click_by_text(page, "다음")

        # 3) 팀장 인센티브
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / "03_framing.png"), full_page=True)
        print("✅ 03 framing")

        await click_by_text(page, "다음")

        # 4) 팀 구성
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / "04_team.png"), full_page=True)
        print("✅ 04 team")

        # 멀티셀렉트로 2명 선택은 어렵게 동작 - 스킵하고 마지막 결과 보여주기
        # 임시로 멀티셀렉트에 값 채우기 시도
        try:
            await page.evaluate("""
                // Streamlit multiselect — first 2 options
                const inputs = document.querySelectorAll('[data-baseweb="select"] input');
                if (inputs.length > 0) {
                    inputs[0].click();
                }
            """)
        except Exception:
            pass

        await browser.close()
        print(f"\n저장 위치: {OUT}")


asyncio.run(main())
