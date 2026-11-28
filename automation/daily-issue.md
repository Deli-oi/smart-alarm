You are running Eli's daily "Wake-Up" automation (scheduled 5:37 am America/New_York). Goal: write today's issue and day plan into his MongoDB Atlas database so his app can show them at 7:00. Do not ask questions; if something is unavailable, do the rest and say what was skipped in your final message. This automation only READS Gmail and Calendar. Never send, reply, delete, label or edit anything anywhere.

SETUP
- Today's date D (America/New_York) as YYYY-MM-DD.
- Load the MongoDB Atlas tools with ToolSearch if needed. Call remote-atlas-connect with projectId 6b08e756a5de7d669fd15af7 and clusterName Smart-Alarm. Use database "smart_alarm" and the returned connectionId.
- If collection "issues" already has a document with date D (use count), skip steps 1-2 and continue from step 3.

1. READINGS. WebFetch https://bible.usccb.org/readings.rss and find the item whose link ends with MMDDYY.cfm for D (some feast days have extra navigation-only items; use the one with reading text). For each of Reading 1, Responsorial Psalm, Gospel (and Reading 2 if present) record label, citation, and a 2 to 3 sentence PARAPHRASE in your own words. Never copy the reading text verbatim. If the feed has no item for D, use the standard lectionary citations if you are sure of them, and say so in the text; otherwise leave readings to the citation you can verify.

2. ISSUE. Target about 2,750 words in total (15 minutes). Use web search for real, recent, cited-in-your-head sources; paraphrase, never copy. Exactly three articles:
   - kind "missed_news": the most important thing from the last 24 to 48 hours that a busy CS student working in procurement would want to know (tech, economy, business). Explain why it matters.
   - kind "research": a recent paper or finding in today's field, chosen by weekday: Mon career (CS, supply chain, executive function), Tue body (training, nutrition, hormonal and metabolic health), Wed law (tax, patent, financial, contract, insurance), Thu mind (cognition, learning), Fri money (risk, unforeseen expenses, international business), Sat and Sun: whichever of these fits the week. Name the study, say what it found and its limits.
   - kind "wildcard": something surprising and true that rewards curiosity.
   Plain, warm, concrete writing; real numbers; no hype; each article about 700 to 850 words. "reflection": 2 sentences connecting today's readings to the day. "critical": an array, empty on almost all days; only add a sentence if there is a genuinely critical development (major market or safety event, or something in his own inbox needing action today).
   Write 8 multiple-choice questions on the readings and the three articles (4 choices each, exactly one correct, vary the position of the right answer). Each question: id "q0".."q7", prompt, choices (array of 4 strings), answer_index (0 to 3).
   Issue document shape (insert with insert-many into collection "issues", exactly these field names):
   {"date": D, "readings": [{"label": str, "reference": str, "text": str}], "reflection": str, "critical": [], "articles": [{"kind": "missed_news"|"research"|"wildcard", "title": str, "body": str}], "questions": [{"id": str, "prompt": str, "choices": [str,str,str,str], "answer_index": int}]}

3. DAY PLAN. Google Calendar list_events for D from 00:00 to 24:00. Timed events become {"start": "HH:MM", "end": "HH:MM", "title": str, "location": str, "all_day": false} in local 24-hour time; put all-day items in "notes" text instead. Gmail search_threads query "in:inbox newer_than:2d" pageSize 10: keep up to 6 that matter to him (skip promotions and automated receipts), each {"sender": str, "subject": str}. delete-many from "day_plans" where date is D, then insert-many one document: {"date": D, "events": [...], "mail": [...], "notes": str}.

4. TASKS. Find yesterday's tasks in collection "tasks" (date = D minus one day) with status "open" or "not_done"; copy each to D as a new document with id "D:tN" (N from 1), status "open", note "Carried over", push_to "", source "". Add up to 3 new tasks only if something in today's calendar or inbox clearly needs action; set source "gmail" or "calendar" and note "Suggested". Skip tasks for D that already exist (same title). Task document shape: {"id": str, "date": D, "title": str, "status": "open", "note": str, "push_to": "", "source": str}.

5. CHECK. count the new documents back, and finish with a short report: what was written, what was skipped and why.
