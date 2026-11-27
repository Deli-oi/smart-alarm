import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":430,"height":900})
        logs=[]; pg.on("console", lambda m: logs.append(m.text)); pg.on("pageerror", lambda e: logs.append("ERR "+str(e)))
        await pg.goto("http://localhost:8000/index.html")
        await pg.evaluate("localStorage.setItem('wk', JSON.stringify({url:'http://localhost:8765',token:'testtok'}))")
        await pg.reload(); await pg.wait_for_timeout(1500)
        txt = await pg.inner_text("#app"); print("HOME:", "Live" in txt, "Retrieval" in txt or "Daniel" in txt or "Placeholder" in txt)
        await pg.evaluate("readDone=true;go('recall')")
        # attempt 1: all wrong (choose index 3)
        for i in range(8):
            await pg.click(f".opt:nth-of-type(4)"); await pg.click(".cta")
        await pg.wait_for_timeout(800)
        print("A1:", (await pg.inner_text("#app")).replace("\n"," | ")[:120])
        await pg.click("text=Second attempt")
        right=[0,1,0,1,1,0,1,1]
        for i in right:
            await pg.click(f".opt:nth-of-type({i+1})"); await pg.click(".cta")
        await pg.wait_for_timeout(800)
        print("A2:", (await pg.inner_text("#app")).replace("\n"," | ")[:120])
        await pg.click("text=Open Today"); await pg.wait_for_timeout(300)
        today=(await pg.inner_text("#app")).replace("\n"," | "); print("TODAY:", today[:400])
        await pg.evaluate("go('evening')"); print("EVE:", (await pg.inner_text("#app")).replace("\n"," | ")[:250])
        await pg.screenshot(path="/tmp/live_today.png")
        print("LOGS:", logs[:5])
        await b.close()
asyncio.run(main())
