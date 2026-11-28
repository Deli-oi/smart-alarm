# What the research says about waking up

Done 28 November 2026, to check the morning flow against the evidence rather than against
intuition. Sources are named so you can go and disagree with them.

## Sleep inertia, the thing the whole 7:00 flow is fighting

Sleep inertia is the grogginess and measurably worse cognition right after waking. The numbers
that matter here:

- It usually runs **15 to 30 minutes**, can reach an hour, and occasionally several hours if
  you are sleep deprived or woke from deep sleep. NIOSH puts the common range at 30 to 60
  minutes. (Wikipedia, *Sleep inertia*, summarising the literature; CDC/NIOSH shift-work module;
  Hilditch & McHill, *Sleep inertia: current insights*, Nature and Science of Sleep 2019.)
- It is **strongest at the moment of waking** and falls away quickly after that. (Santhi et al.,
  *Morning Sleep Inertia in Alertness and Performance*, PLOS ONE 2013.)
- How bad is it? On cognitively demanding tasks, performance immediately after waking has been
  found **worse than after 26 hours of sleep deprivation**. (Reviewed in *Effects of Sleep Inertia
  on Cognition*.) That is the single most useful number in this document.
- Nothing yet tested reliably clears it **inside the first 15 minutes**. (Hilditch et al.,
  *Can Exercise Reduce Sleep Inertia?*, Frontiers in Physiology 2020.)

## The awkward finding for this app

Memory is measurably worse **when learning happens immediately after waking**, and worse again
when the waking came out of deep sleep rather than light sleep. (Research summarised under
*Sleep Inertia*, Tassi & Muzet and related work.)

So the 15-minute issue and an 8-question recall gate, run at 7:00 to 7:15, sit in the worst
cognitive window of the entire day.

The counterweight is real, though: morning genuinely is the best time to learn. Encoding capacity
**decays across a day of being awake and is restored by sleep**, so the hours after waking beat
the evening for taking something in. (Mander et al., *Wake deterioration and sleep restoration of
human learning*, Current Biology 2011.)

Both things are true. The morning is the right part of the day; the first fifteen minutes of it
is the wrong part of the morning. The fix is not to move the reading to the afternoon. It is to
move it twenty or thirty minutes later and spend that time waking up properly.

## What actually helps, ranked by how well it is supported

1. **Caffeine** is the best-supported countermeasure, but taken *after* waking its effect is
   delayed: it shortens the tail of sleep inertia and does nothing for the worst early minutes.
   (Hilditch & McHill 2019.) Coffee at 7:35 helps the rest of the morning, not the quiz.
2. **Brief breathing and muscular work.** A 2026 Frontiers in Physiology study calls
   "physiological dynamization", short respiratory and muscular exercises, a highly promising
   reactive countermeasure for rapidly dissipating sleep inertia. This is the only thing in the
   literature that plausibly acts inside the first few minutes.
3. **A task you must complete to dismiss the alarm.** A JMIR Formative Research study (2022) on
   wake-up tasks found that requiring a small assignment, a maths problem or taking a photo,
   before the alarm could be dismissed was significantly associated with actually doing the
   target behaviour afterwards (maths p=.005, picture p<.001). **This is the recall gate, and it
   has evidence behind it.**
4. **Light.** Weaker than folklore suggests. Blue-enhanced white light alone was not sufficient to
   reduce sleep inertia in Santhi et al. 2013. Worth doing for circadian anchoring; do not expect
   it to wake you up.

## Snoozing is not the sin it is made out to be

The 7:10 safety alarm is, in effect, a snooze, and that turns out to be fine. Sundelin et al.,
*Is snoozing losing?* (Journal of Sleep Research, 2024), ran a polysomnography study on 31
habitual snoozers and found 30 minutes of snoozing **improved or did not affect** cognitive
performance on rising compared with an abrupt awakening, without substantially disturbing sleep,
particularly for late chronotypes and people who wake groggy. Keep the safety alarm.

## What was changed because of this

- **Sixty seconds of standing and breathing before the issue opens.** Tapping Morning Issue now
  goes to a breathing count first, not straight to the reading. It is the only countermeasure
  with support inside the first few minutes, and it is skippable, because a gate you resent is a
  gate you stop using.
- **A dark theme that follows the phone.** A cream screen at 7:00 in a dark room is punishing, and
  the evidence on morning light says it is not buying the alertness it costs in comfort.
- **The safety alarm stays**, now on purpose rather than by default.

## What is proposed and not done

**Move the reading later, keep the wake time.** Wake at 7:00, spend the first twenty to thirty
minutes on the things that do not need a working brain, and read at about 7:30 when inertia has
lifted. That collides with the protected 7:35 to 8:00 breakfast block, so it is a real decision
about the shape of the morning, not a code change, and it is Eli's to make.

Three ways it could go:

1. Breakfast first at 7:05, read and recall at 7:35. Caffeine has also had half an hour to work.
2. Keep breakfast at 7:35 and read from 8:00.
3. Leave it as it is, and accept that the recall gate is hard on purpose. Difficulty is the
   mechanism: the JMIR result is about a task you must finish, and an easy one would not work.


---

# Part two: the research the industry funds

Looked at on 28 November 2026, on the question of whether the wake-up and wellness app
category's own evidence supports building like they build.

## The short answer

Two of the category's signature features are weakly supported, and the thing that is strongly
supported is one almost nobody sells.

## Smart alarms: the premise is sound, the sensing is not

Every app in the category sells the same promise. Sleep Cycle's own page says it works by
"detecting when the best time to wake up is, by gently waking users up in their lightest sleep
phase", using a 30-minute window and patented sound analysis of movement in bed.

The underlying claim is reasonable: waking from deep sleep gives worse sleep inertia than waking
from light sleep, which Part One already establishes. The problem is the measurement. A 2021
validation study found consumer sleep trackers agreed with polysomnography on sleep stage only
**50 to 86 percent of the time**, depending on stage and device, and phone microphone and
accelerometer methods sit at the weak end of that range. An alarm firing on a coin-flip-to-decent
guess about your sleep stage is not the precision instrument the marketing implies.

Most of what is written about this is affiliate content rather than research. Several pages
confidently cite a 2024 study as confirmation; the pages making that claim are commercial sleep
product blogs, so take it as unverified.

**What this means for us:** do not build sleep-stage detection. A fixed 7:00 alarm with a safety
alarm behind it avoids the whole problem, and regularity (below) is worth more than stage-timing
anyway.

## Mindfulness apps: real but small, and half the trials have a conflict

The cleanest thing in this literature is a systematic review that audited the funding rather than
just the findings: O'Daffer et al., *Efficacy and Conflicts of Interest in RCTs Evaluating
Headspace and Calm Apps* (JMIR Mental Health, 2022).

- 14 RCTs of Headspace, 1 of Calm.
- Headspace improved depression in 75% of the studies measuring it.
- **50% (7 of 14) of the Headspace trials reported a conflict of interest involving the company.**
  The most common was the company giving participants free premium access; 2 of 14 had a Headspace
  employee involved.

Where effects are measured carefully by independent teams, they are real and small. A multisite
RCT in health care workers found Headspace reduced stress more than the comparator with **small
effect sizes** that "could have population-level benefits". A 2026 RCT on sleep found longer sleep
duration at one of three measurement points (p=.04) and no difference at the other two.

**What this means for us:** be suspicious of any single impressive number from a company that
sells the thing, including ours. The honest expectation for a personal morning app is a small
effect that depends entirely on actually using it.

## The thing almost nobody sells: regularity

This is the strongest finding of the whole search, and it points away from what the products
measure.

Windred et al., *Sleep regularity is a stronger predictor of mortality risk than sleep duration*
(Sleep, 2024) used objective actigraphy from **over 60,000 people** in the UK Biobank and found
that day-to-day consistency of sleep and wake timing predicted all-cause mortality **better than
how long people slept**, with risk reductions of 20 to 48 percent across the top four regularity
quintiles. A companion commentary calls it out directly: regularity predicting mortality more
strongly than duration "inverts the emphasis of most sleep advice and of most sleep tracking
products."

**What this means for us:** the number worth showing is not hours slept or sleep stages. It is
whether he starts his morning at the same time every day.

## And the risk that kills personal apps

Eysenbach's "law of attrition" (JMIR, 2005) is the observation that in any eHealth trial a
substantial proportion of users stop using the application. Attrition in digital health
interventions runs **50 to 80 percent**.

The most likely way this project fails is not a bug. It is that he stops opening it in March.
That argues for keeping the daily cost low, making the gate skippable, and measuring consistency
rather than performance.

## What was changed because of part two

- **A start-time consistency line on the home screen**, from a new `/regularity` endpoint: how
  many mornings in the last fourteen, the usual time, and how many were within half an hour of
  it. Written as plain counts, not a score, and not framed as a streak: a streak is a thing you
  protect, and the habit is the point.
- **Recall attempts are now timestamped**, which is what makes the above measurable at all.
- **Sleep-stage detection stays unbuilt**, on purpose, with the reason written down.
