"""End-to-end check of the preview against a running backend.

    cd backend && STORE=memory DEBUG=true API_TOKEN=testtok python -m uvicorn app.main:app --port 8765
    cd site && python -m http.server 8000
    python scripts/e2e_ui.py

Drives real clicks in headless Chrome: connect through the Settings screen, read the issue,
fail the recall, pass it on the second attempt, then open Today and the Evening Check.
Exits non-zero on the first failed expectation.
"""

import asyncio
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:8000/index.html"
API = "http://localhost:8765"
TOKEN = "testtok"
fails: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("  ok   " if ok else "  FAIL ") + name + ((" — " + detail) if detail and not ok else ""))
    if not ok:
        fails.append(name)


async def main() -> int:
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 430, "height": 900})
        # Script errors are failures. Failed requests are not: this run deliberately sends a
        # wrong token and reads endpoints the server has no data for yet.
        errors: list[str] = []
        requests: list[str] = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: requests.append(m.text) if m.type == "error" else None)

        await pg.goto(URL)
        await pg.wait_for_timeout(400)
        check("sample content loads", "Wake-Up" in await pg.inner_text("#app"))

        # --- settings: type the server in by hand, the way he will on the phone
        print("settings")
        await pg.click("text=Settings")
        await pg.wait_for_selector("#su")
        await pg.fill("#su", "")
        await pg.type("#su", "localhost:8765")  # no scheme, as typed on a phone
        await pg.fill("#st", TOKEN)
        check("token is masked by default", await pg.get_attribute("#st", "type") == "password")
        await pg.click("button[aria-pressed='false']")
        check("Show reveals the token", await pg.get_attribute("#st", "type") == "text")
        check("url field skips autocapitalise", await pg.get_attribute("#su", "autocapitalize") == "off")
        check("url field has a label", await pg.locator("label[for='su']").count() == 1)

        await pg.click("#sv")
        await pg.wait_for_timeout(2500)
        txt = await pg.inner_text("#app")
        check("scheme-less address still connects", "Connected to localhost:8765" in txt, txt[:160])
        check("checks are listed", "Server answers" in txt and "Token accepted" in txt)

        # --- a wrong token must say so instead of silently showing samples
        await pg.fill("#st", "wrong-token")
        await pg.click("#sv")
        await pg.wait_for_timeout(2500)
        txt = await pg.inner_text("#app")
        check("bad token is named", "Token refused" in txt, txt[:160])

        await pg.fill("#st", TOKEN)
        await pg.click("#sv")
        await pg.wait_for_timeout(2500)

        # --- the morning run
        print("morning")
        await pg.click("text=‹ Notes")
        await pg.wait_for_timeout(300)
        home = await pg.inner_text("#app")
        check("home shows live mode", "Live" in home, home[:160])

        await pg.click("text=Morning Issue")
        await pg.wait_for_timeout(300)
        check("issue renders articles", "Antikythera" in await pg.inner_text("#app"))

        await pg.evaluate("readDone=true;go('recall')")
        await pg.wait_for_timeout(300)
        for _ in range(8):  # every answer wrong
            await pg.click(".opt:nth-of-type(4)")
            await pg.click(".cta")
        await pg.wait_for_timeout(1500)
        txt = await pg.inner_text("#app")
        check("first attempt fails", "Second attempt" in txt, txt[:160])

        await pg.click("text=Second attempt")
        await pg.wait_for_timeout(300)
        for i in [0, 1, 0, 1, 1, 0, 1, 1]:  # the demo issue's answers
            await pg.click(f".opt:nth-of-type({i + 1})")
            await pg.click(".cta")
        await pg.wait_for_timeout(1500)
        txt = await pg.inner_text("#app")
        check("second attempt unlocks the day", "The day is open" in txt, txt[:160])

        await pg.click("text=Open Today")
        await pg.wait_for_timeout(300)
        today = await pg.inner_text("#app")
        check("breakfast block is protected", "Breakfast" in today)
        check("calendar events show", "Lecture" in today, today[:200])
        check("overlapping events are flagged", "overlap" in today, today[:300])

        await pg.evaluate("go('evening')")
        await pg.wait_for_timeout(300)
        eve = await pg.inner_text("#app")
        check("evening check lists tasks", "Reply to the recruiter" in eve, eve[:200])
        check("auto-detected work is marked", "Detected" in eve, eve[:200])

        await pg.evaluate("go('mail')")
        await pg.wait_for_timeout(300)
        check("mail from the day plan", "Interview scheduling" in await pg.inner_text("#app"))

        await pg.evaluate("go('files')")
        await pg.wait_for_timeout(300)
        check("empty files screen explains itself", "Nothing recent" in await pg.inner_text("#app"))

        # --- forgetting the server goes back to samples
        await pg.evaluate("go('settings')")
        await pg.wait_for_timeout(300)
        await pg.click("text=Forget this server")
        await pg.wait_for_timeout(800)
        check("forget returns to sample content", "Not connected" in await pg.inner_text("#app"))

        await pg.screenshot(path="/tmp/ui_settings.png", full_page=True)
        check("no script errors", not errors, "; ".join(errors[:3]))
        print(f"  note  {len(requests)} failed requests, expected from the wrong-token check")
        await b.close()

    print("\n" + ("all checks passed" if not fails else f"{len(fails)} failed: " + ", ".join(fails)))
    return 1 if fails else 0


sys.exit(asyncio.run(main()))
