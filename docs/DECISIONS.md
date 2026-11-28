# Development choices

Why the system is shaped the way it is. Read this before changing the daily flow: several of
these look like oversights until you know the reason. Newest first.

## Everything waits for the 10:30 run, to save usage

*28 November 2026.* The app can ask for the day log to be acted on early: "Send it to Claude now"
sets `process_requested` on the day's `day_log` document. **Nothing polls for that flag.** The
only thing that reads it is the 10:30 evening run, which honours it and then clears it.

The button marks the day's entries with a `sent_at` stamp and the app moves them below the
button under a tick, so handing over is visible. A tick means handed over, not acted on.

An on-demand run would need a scheduled task firing on a short cycle, and the floor for those is
hourly, which is 24 sessions a day against the account's usage. Eli decided to keep every update
on the single 10:30 run for now rather than spend that.

So the flag is best read as "he wanted this sooner", not as a trigger. If an agent later adds a
poller, update this entry and `docs/AUTOMATION.md` together, and say what the usage costs.

## No sleep-stage detection, ever, on a phone

*28 November 2026.* The category's signature feature is an alarm that fires when it thinks you
are in light sleep. Consumer trackers agree with polysomnography on sleep stage only 50 to 86
percent of the time, and phone microphone methods are the weak end of that. A fixed 7:00 alarm
with the 7:10 safety behind it avoids the guesswork entirely. If this is ever revisited, it
should be on real wearable data, not a microphone.

## Consistency is the number on the home screen

*28 November 2026.* Day-to-day regularity of sleep and wake timing predicts mortality better
than sleep duration does, in 60,000 people with objective measurement. It is also the only thing
of that calibre this app can actually see, through the minute he starts each morning.

Shown as plain counts, never a score, and deliberately not a streak. Attrition in digital health
runs 50 to 80 percent, so the real risk is that he stops opening it, and a streak that breaks is
a reason to stop. `docs/RESEARCH.md` part two has the sources.

## Sixty seconds of breathing before the issue

*28 November 2026.* Tapping Morning Issue goes to a wake step first: stand up, curtains, sixty
seconds of paced breathing. Then the reading.

This is the only countermeasure in the literature with support inside the first few minutes of
waking; caffeine is better overall but its effect is delayed, and light is weaker than folklore
claims. It is skippable on purpose. A gate he resents is a gate he stops using, and the recall
gate is already the hard thing in this morning. `docs/RESEARCH.md` has the sources.

## The theme follows the phone

*28 November 2026.* A cream page at 7:00 in a dark bedroom is punishing, and the evidence that
morning screen light buys alertness is weak, so there is nothing to trade away by going dark. The
app now follows `prefers-color-scheme` rather than forcing either one: claret becomes a fill-only
colour on dark, where it has no contrast as text, and brass carries the interactive labels.

## The lock is built but switched off

*28 November 2026.* `ENFORCE_GATE` makes the recall gate real: with it on, `/day` and
`/tasks/today` answer 423 until the day's quiz is passed or a skip is on the record. It defaults
to **off**, and the app's own lock stays cosmetic until it is turned on.

The reason is asymmetry. A gate that fails open costs nothing much; a gate that falsely locks
costs a morning, and the morning flow has run exactly once. Turn it on in Railway once a week of
mornings has gone through cleanly.

## Early fish loading based on one step before

*28 November 2026.* Fish takes about three seconds to generate the rundown. Starting that when he
taps Play is three seconds of dead air, and the first version also let a second tap start a second
clip playing over the first.

The audio now starts loading **one step before the place it is needed**: rendering the second to
last recall question calls `earlyFishLoad()`, so the clip is in hand by the time the day opens.

The rule, if the flow changes: the trigger is *one step before the need*, not a fixed question
number. Add or remove a step and the call moves to whatever is now one step before Today. The
prefetch must stay silent, happen at most once a morning, and be free to fail; `speak()` falls back
to fetching normally, and waits on an in-flight prefetch rather than starting a second one.

The cost is one Fish generation on a morning where he reaches the end of recall and never taps
Play. That was accepted in exchange for the audio being instant when he does.

Implemented in `preview/template.html` under the comment of the same name, and covered by four
checks in `scripts/e2e_ui.py`.

## The backend never calls Claude

*28 November 2026.* No `ANTHROPIC_API_KEY`. Scheduled tasks on Eli's own Claude account do the
reading and writing, through his connectors, and put documents straight into Atlas; the backend
only reads and grades. This was a cost decision and it shapes everything: the backend's own 6:00
issue job returns immediately when no key is set. See `docs/AUTOMATION.md`.

## The evening check creates, and never sends

*28 November 2026.* The evening run may create calendar events, Gmail drafts and tasks from the
day log. It may never send mail, reply, delete, decline an invitation or edit a file. A draft is
as far as it goes, and he sends it himself. Anything a note asks for beyond that is reported in
the summary and left undone.

## Two schedulers, in a fixed order

*28 November 2026.* The backend's own evening job runs at 22:20 and only marks tasks done; the
Claude-account automation runs at 22:27 and has the last word on the summary. The backend job
returns immediately when it has no source configured. Without that guard it overwrote the
automation's summary with an emptier one, which is exactly what happened on the first night.

## No calendar link and no mail password

*28 November 2026.* `ICS_URL` and the Gmail app password belong to an earlier design where the
backend read the calendar and inbox itself. The automation reads both through connectors instead.
The code paths still exist and are still tested, so a future deployment can turn them back on, but
they are not part of the running system.

---

## The service worker fetches network first

*28 November 2026.* The Home Screen install caches the page so it opens without a connection, but
network first with the cache as fallback, not the other way round. Cache first would keep serving
a stale app for days after a push, and this page changes far more often than it is opened.

# Wanted next

Not built. Recorded so the shape is not lost.

## Route tasks to the right worker

When a note names something that another system should do, hand it to that system instead of
making a task for him. Booking a flight or a reservation is the clearest case. The routing targets
Eli has in mind are the agents he already runs, local models, and muse agents.

This needs three things that do not exist yet: a way to tell from a note which worker should take
it, a record of which workers are reachable and what each one is allowed to do, and a result that
comes back into the day's record so the evening summary can say what was actually done. Until
then, every such note becomes a task on tomorrow's list.
