"""Streamlit 앱 스크린샷 (큰 사이즈 + 상단 포커스)"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path(__file__).parent / "screenshots"
OUT.mkdir(exist_ok=True)


async def click_next(page):
    try:
        btn = page.get_by_role("button", name="다음")
        await btn.first.click(timeout=3000)
        await page.wait_for_timeout(1800)
    except Exception:
        pass


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 1100, "height": 850},
            device_scale_factor=2,
        )
        page = await ctx.new_page()
        await page.goto("http://localhost:8501", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(2200)

        # 1) 인트로
        await page.screenshot(path=str(OUT / "01_intro.png"), clip={"x": 0, "y": 0, "width": 1100, "height": 850})
        print("✅ 01")

        # 시작 버튼
        try:
            await page.get_by_role("button", name="시작하기").first.click()
            await page.wait_for_timeout(1800)
        except Exception:
            pass

        # 2) 출석
        await page.screenshot(path=str(OUT / "02_attendance.png"), clip={"x": 0, "y": 0, "width": 1100, "height": 850})
        print("✅ 02")
        await click_next(page)

        # 3) 인센티브 프레이밍
        await page.screenshot(path=str(OUT / "03_framing.png"), clip={"x": 0, "y": 0, "width": 1100, "height": 850})
        print("✅ 03")
        await click_next(page)

        # 4) 팀 구성
        await page.screenshot(path=str(OUT / "04_team.png"), clip={"x": 0, "y": 0, "width": 1100, "height": 850})
        print("✅ 04")

        await browser.close()
        print(f"\n저장: {OUT}")


asyncio.run(main())
