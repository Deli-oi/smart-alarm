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
        check("the wake step comes first", "Stand up" in await pg.inner_text("#app"))
        await pg.click("text=I'm already up")
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

        # --- early fish loading based on one step before
        print("voice")
        speaks: list[str] = []
        pg.on("request", lambda r: speaks.append(r.url) if "/jarvis/speak" in r.url else None)
        await pg.evaluate("boot()")
        await pg.wait_for_timeout(2000)
        await pg.evaluate("readDone=true;go('recall')")
        await pg.wait_for_timeout(300)
        total = await pg.evaluate("DATA.quiz.length")
        for _ in range(total - 3):  # stop one short of the second to last question
            await pg.click(".opt:nth-of-type(1)")
            await pg.click(".cta")
            await pg.wait_for_timeout(60)
        check("nothing fetched before the trigger", len(speaks) == 0, f"{len(speaks)} early")

        await pg.click(".opt:nth-of-type(1)")
        await pg.click(".cta")  # lands on the second to last question
        await pg.wait_for_timeout(1500)
        check("second to last question starts the fetch", len(speaks) == 1, f"{len(speaks)} requests")
        check("the fetch is silent", await pg.evaluate("voiceState") == "")
        check("the audio is in hand", bool(await pg.evaluate("voiceUrl")))

        await pg.evaluate("unlocked=true;go('today')")
        await pg.wait_for_timeout(300)
        mark = len(speaks)
        await pg.locator("[data-voice]").click()
        await pg.wait_for_timeout(1000)
        check("playing reuses the prefetch", len(speaks) == mark, f"{len(speaks) - mark} extra")
        await pg.evaluate("stopSpeech()")

        # --- and with nothing prefetched, two taps must still make one request
        await pg.evaluate("boot()")
        await pg.wait_for_timeout(2000)
        await pg.evaluate("unlocked=true;go('today')")
        await pg.wait_for_timeout(300)
        mark = len(speaks)
        btn = pg.locator("[data-voice]")
        await btn.click()
        await btn.click()  # the double tap that used to play it twice, over itself
        await pg.wait_for_timeout(1500)
        check("two taps make one request", len(speaks) - mark <= 1, f"{len(speaks) - mark} requests")
        check("voice state is not stuck", await pg.evaluate("voiceState") in ("", "loading", "playing"))
        await pg.evaluate("stopSpeech()")

        # --- the day log
        print("day log")
        await pg.evaluate("go('log')")
        await pg.wait_for_timeout(300)
        await pg.fill("#jt", "move the gym to six and draft a yes to Alyssa")
        posts: list[str] = []
        pg.on("request", lambda r: posts.append(r.url) if r.url.endswith("/notes") and r.method == "POST" else None)
        await pg.click("#jsave")
        await pg.click("#jsave")  # same guard, different button
        await pg.wait_for_timeout(1500)
        check("one note per tap", len(posts) == 1, f"{len(posts)} posts")
        txt = await pg.inner_text("#app")
        check("the note is listed", "move the gym to six" in txt, txt[:200])

        await pg.reload()
        await pg.wait_for_timeout(2500)
        await pg.evaluate("go('log')")
        await pg.wait_for_timeout(400)
        check("the note survives a reload", "move the gym to six" in await pg.inner_text("#app"))

        # --- handing the day over: the entry has to visibly move, below the button, ticked
        sends: list[str] = []
        pg.on("request", lambda r: sends.append(r.url) if "/notes/process-now" in r.url else None)
        btn = pg.locator("#jsend")
        check("the send button is live while something waits", await btn.is_enabled())
        # Two taps in the same tick, which is what a real double-tap is: the button has not
        # been re-rendered as disabled yet, so only the in-code guard can stop the second.
        await pg.evaluate("processNow();processNow()")
        await pg.wait_for_timeout(1800)
        check("a double tap hands over once", len(sends) == 1, f"{len(sends)} posts")

        txt = await pg.inner_text("#app")
        check("the hand-over is confirmed", "10:30 run acts on it" in txt, txt[:200])
        check("the entry is ticked", "\u2713" in txt, txt[:200])
        check("it moved to handed over", "Handed over" in txt and "Waiting," not in txt, txt[:200])
        check("the button stops offering", not await btn.is_enabled())

        # the confirmation must sit below the button he pressed, not above it
        order = await pg.evaluate(
            "(()=>{const b=document.querySelector('#jsend');"
            "const h=[...document.querySelectorAll('h2')].find(e=>e.textContent.startsWith('Handed over'));"
            "return h? b.compareDocumentPosition(h) & Node.DOCUMENT_POSITION_FOLLOWING ? 'below':'above' : 'missing'})()"
        )
        check("handed-over entries render below the button", order == "below", order)

        await pg.reload()
        await pg.wait_for_timeout(2500)
        await pg.evaluate("go('log')")
        await pg.wait_for_timeout(400)
        txt = await pg.inner_text("#app")
        check("the hand-over survives a reload", "Handed over" in txt and "\u2713" in txt, txt[:200])

        await pg.evaluate("go('home')")
        await pg.wait_for_timeout(300)
        check("the note button is on every screen", await pg.locator(".jot").count() == 1)

        # --- forgetting the server goes back to samples
        await pg.evaluate("go('settings')")
        await pg.wait_for_timeout(300)
        await pg.click("text=Forget this server")
        await pg.wait_for_timeout(800)
        check("forget returns to sample content", "Not connected" in await pg.inner_text("#app"))

        # --- a diagram from the database must render, and must not carry script with it
        hostile = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 40' onload='window.__x=1'>"
                   "<script>window.__y=1</script><rect x='2' y='2' width='96' height='36' fill='none' "
                   "stroke='currentColor'/><text x='50' y='25' text-anchor='middle'>cache</text>"
                   "<a href='javascript:window.__z=1'><circle cx='10' cy='10' r='3'/></a></svg>")
        await pg.evaluate(
            "s => { DATA.articles[0].svg = s; go('issue'); }", hostile
        )
        await pg.wait_for_timeout(300)
        check("the diagram renders", await pg.locator("figure.fig svg").count() == 1)
        check("its label survives", "cache" in await pg.inner_text("figure.fig"))
        check("the onload attribute is stripped", await pg.evaluate("window.__x === undefined"))
        check("the script element is stripped", await pg.evaluate("window.__y === undefined"))
        check("no script element remains", await pg.locator("figure.fig script").count() == 0)
        anchors = await pg.evaluate(
            "[...document.querySelectorAll('figure.fig [href]')].map(e => e.getAttribute('href'))"
        )
        check("javascript hrefs are stripped", all("javascript:" not in (h or "") for h in anchors), str(anchors))

        # --- the dark theme has to be legible, not just present
        dark = await b.new_page(viewport={"width": 430, "height": 900}, color_scheme="dark")
        await dark.goto(URL)
        await dark.wait_for_timeout(600)
        bg = await dark.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--paper').trim()")
        ink = await dark.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--ink').trim()")
        check("dark theme applies", bg == "#15120d" and ink == "#ece3d2", f"{bg} / {ink}")
        await dark.screenshot(path="/tmp/ui_dark.png")
        await dark.close()

        await pg.screenshot(path="/tmp/ui_settings.png", full_page=True)
        check("no script errors", not errors, "; ".join(errors[:3]))
        print(f"  note  {len(requests)} failed requests, expected from the wrong-token check")
        await b.close()

    print("\n" + ("all checks passed" if not fails else f"{len(fails)} failed: " + ", ".join(fails)))
    return 1 if fails else 0


sys.exit(asyncio.run(main()))
