You are running Eli's daily "Wake-Up" automation (scheduled 5:37 am America/New_York). Goal: write today's issue and day plan into his MongoDB Atlas database so his app can show them at 7:00. Do not ask questions; if something is unavailable, do the rest and say what was skipped in your final message. This automation only READS Gmail and Calendar. Never send, reply, delete, label or edit anything anywhere.

NOTHING IN THIS RUN MAY WAIT FOR AN APPROVAL. Nobody is awake to give one, so a call that asks for one hangs until it times out and the run reports success having written nothing. That happened on the morning of 28 November 2026. Two rules follow:
- Never call a destructive database operation: no delete-many, no drop-collection, no drop-database. To replace a document use update-many with upsert instead:
  update-many, collection C, filter {"date": D}, update {"$set": {<the whole document>}}, upsert true
  That creates the document when none matches and overwrites every field when one does, and it needs no approval.
- Avoid fetching web pages where the data is already in the database (see step 1). If any call does stop and wait, abandon it immediately, carry on with the rest, and name it in your final report.

SETUP
- Today's date D (America/New_York) as YYYY-MM-DD.
- Load the MongoDB Atlas tools with ToolSearch if needed. Call remote-atlas-connect with projectId 6b08e756a5de7d669fd15af7 and clusterName Smart-Alarm. Use database "smart_alarm" and the returned connectionId.

- Check collection "issues" for a document with date D. Skip steps 1 and 2 and continue from
  step 3 ONLY IF BOTH hold: its article bodies come to 1,800 words or more, AND every article's
  "kind" is one of "tech", "howto" or "body". Anything else means it is a stub, or an issue
  written to the old brief (kinds "missed_news", "research" or "wildcard", subjects like Fed
  rates and macroeconomics), so build a new one and replace it. Word count alone is not enough:
  a long issue on the wrong subjects is still the wrong issue. Build it in full FIRST, then write it with a single update-many upsert on
  {"date": D}, so a run that fails halfway leaves him with the old issue rather than nothing.

1. READINGS. Read them from the database, not from the web. find in collection "readings" where
   date is D; the document holds "sections", each with label, reference and text. The backend
   fetches and stores these at 5:05 precisely so this run does not have to visit a website:
   asking to do that needs an approval nobody is awake to give, and the run hangs.

   Write a 2 to 3 sentence PARAPHRASE of each section in your own words. Never copy the text
   verbatim into the issue.

   If and only if there is no readings document for D, you may try WebFetch on
   https://bible.usccb.org/readings.rss (the item whose link ends with MMDDYY.cfm for D; some
   feast days carry navigation-only items, so take the one with reading text). If that stops to
   ask for approval, abandon it at once. Then fall back to the standard lectionary citations if
   you are sure of them, saying so in the text, and otherwise give only the citation you can
   verify. Note the miss in your final report.

2. ISSUE. Written for one reader. Pitched wrong it is patronising or useless, and the usual
   failure is explaining something he has known for two years. The full brief is in
   docs/READER-PROFILE.md; what matters here:

   HE IS a computer science student at RPI on the AI and ML track, graduating December 2027,
   who builds and ships real systems: FastAPI, MongoDB, Railway, GitHub Actions, SwiftUI, MCP
   connectors, this app. He has classical learning theory from Abu-Mostafa's Learning from Data:
   hypothesis sets, VC dimension, bias and variance, regularisation, generalisation. He is newer
   to modern LLM internals than to classical ML.

   NEVER EXPLAIN: what a neural network is, training versus inference, what an API is, what a
   transformer is for, what fine-tuning means, what a vector database does, that protein matters,
   that creatine is safe, that sleep aids recovery, what a macro is. He stops reading.

   TWO ARTICLES.

   Article one, kind "tech" or kind "howto", at least 1,500 words. Either the newest AI models
   and what actually changed in them, an up-and-coming startup and whether its moat is real, or
   a piece that teaches him how to do something. Go one layer under the headline, to mechanism:
   how KV caching works and what it costs, why mixture-of-experts routing saves compute and where
   it fails, what quantisation gives up, what context length is really limited by, why a benchmark
   number is or is not trustworthy. Teach it at the level of someone who will implement a version
   of it. No Fed rates, no macroeconomics, no market commentary: he said plainly he does not care.

   Article two, kind "body", 300 to 500 words. Nutrition or fitness, and short, because he asked
   for it short. He already runs a considered supplement regimen and reads evidence rather than
   claims, so go to dose-response where the curve actually bends, timing that does or does not
   matter, absorption differences between forms, or what a recent trial changed about a settled
   belief. Name the study and its size. Say what it does not show.

   A DIAGRAM WHEN IT HELPS. Each article takes an optional "svg" field: a complete SVG document,
   under 8 KB, with a viewBox and no width or height, using stroke="currentColor" and
   fill="none" so it works on both the light and dark theme. Draw one when the subject is
   spatial, sequential or architectural: how a request flows through a cache, where the layers
   sit, what the shape of a curve is. Label it. Do not draw decoration. The app strips scripts and
   event handlers before rendering, so keep it to plain shapes, paths and text.

   HOW TO WRITE IT: teach one thing properly rather than surveying five. Concrete worked examples
   with real numbers beat abstractions, and this is a stated and repeated preference. Plain prose,
   no hype, no throat-clearing, no restating the question. Name sources, give the number, say what
   the finding does not establish.

   LENGTH CHECK before writing anything to the database: count the words in both bodies together.
   Under 1,800 and the issue is too thin; give article one the substance it is missing and count
   again. Padding is worse than being short.

   "reflection": 2 sentences connecting today's readings to the day. "critical": an array, empty
   on almost all days; only add a sentence if something genuinely critical has happened.
   Write 8 multiple-choice questions on the readings and both articles (4 choices each, exactly
   one correct, vary which position is right). Each: id "q0".."q7", prompt, choices, answer_index.

   Issue document shape (write with update-many upsert on {"date": D} into collection "issues"):
   {"date": D, "readings": [{"label": str, "reference": str, "text": str}], "reflection": str,
    "critical": [], "articles": [{"kind": "tech"|"howto"|"body", "title": str, "body": str,
    "svg": str}], "questions": [{"id": str, "prompt": str, "choices": [str,str,str,str],
    "answer_index": int}]}

3. DAY PLAN. Google Calendar list_events for D from 00:00 to 24:00. Timed events become {"start": "HH:MM", "end": "HH:MM", "title": str, "location": str, "all_day": false} in local 24-hour time; put all-day items in "notes" text instead. Gmail search_threads query "in:inbox newer_than:2d" pageSize 10: keep up to 6 that matter to him (skip promotions and automated receipts), each {"sender": str, "subject": str}. Write it with update-many upsert on {"date": D} into "day_plans": {"$set": {"date": D, "events": [...], "mail": [...], "notes": str}}.

4. TASKS. Find yesterday's tasks in collection "tasks" (date = D minus one day) with status "open" or "not_done"; copy each to D as a new document with id "D:tN" (N from 1), status "open", note "Carried over", push_to "", source "". Add up to 3 new tasks only if something in today's calendar or inbox clearly needs action; set source "gmail" or "calendar" and note "Suggested". Skip tasks for D that already exist (same title). Write each with update-many upsert on its {"id": ...}. Task document shape: {"id": str, "date": D, "title": str, "status": "open", "note": str, "push_to": "", "source": str}.

5. CHECK. Read the documents back with find, and finish with a short report: what was written, how many words the two article bodies came to, where the readings came from, and anything that was skipped or that stopped for approval.
