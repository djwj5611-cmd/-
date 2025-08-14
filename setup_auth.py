# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

# 인증 정보를 저장할 사이트 목록
SITES_TO_LOGIN = [
    'https://www.google.com',
    'https://theqoo.net',
    'https://www.dcinside.com'
]

async def main():
    async with async_playwright() as p:
        # 헤드리스 모드를 False로 설정하여 실제 브라우저 창을 띄웁니다.
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("="*50)
        print("브라우저가 열렸습니다. 아래 사이트에 차례대로 로그인해주세요.")
        print("로그인이 완료되면 다음 사이트로 이동합니다.")
        print("모든 사이트 로그인이 끝나면 브라우저를 닫아주세요.")
        print("="*50)

        for site in SITES_TO_LOGIN:
            print(f"n[로그인 필요] {site} 로 이동합니다...")
            await page.goto(site, timeout=60000)
            # 사용자가 로그인할 시간을 충분히 줍니다.
            # 이 창에서 로그인, 팝업 닫기 등 모든 작업을 완료하세요.
            await page.pause()

        # 모든 사이트 로그인이 완료된 후, 인증 정보를 파일로 저장합니다.
        await context.storage_state(path='auth.json')
        print("n[성공] 인증 정보가 'auth.json' 파일로 저장되었습니다.")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
