# UI review, 28 November 2026

Reviewed `preview/template.html` and `ios/App/Views/` against two skills:

- `anthropics/skills@frontend-design` (the most-starred skills repo on GitHub, about 183k stars) for visual judgement
- `vercel-labs/agent-skills@web-design-guidelines` for the Web Interface Guidelines checklist

Both are installed under `~/.agents/skills/`. Everything below is fixed unless marked **open**.

## Settings, the screen that prompted this

The old screen was two unlabelled inputs and a button.

| Problem | Why it hurt on a phone |
|---|---|
| No `type`, `inputmode` or `autocapitalize` on the address field | iOS capitalised and autocorrected the address, so a correctly typed URL failed |
| No `<label>` on either field | Nothing to tap to focus; nothing for VoiceOver to read |
| Token masked with no reveal | A pasted token could not be checked against the one in Railway |
| No scheme handling | `my-app.up.railway.app` fetched as a relative path and failed oddly |
| No request timeout | A wrong address hung with no feedback; the button looked dead |
| No pending state | Nothing happened visibly between tapping and the result |
| `Promise.all` across four endpoints | One missing endpoint silently dropped the whole app back to samples |
| Errors as `/day 500` | Named no cause and no fix |
| Values written into HTML with an escaper that missed quotes | A token containing `"` broke the field |

Now: labelled fields, `type="url" inputmode="url"` with autocapitalise, autocorrect and spellcheck off,
a Show toggle on the token, the scheme added automatically (http only for localhost), a 12-second
timeout, a Connecting… state, and a per-endpoint checklist that distinguishes an unreachable server,
a refused token and an issue that simply has not been written yet.

## Across every screen

- `preview/template.html` — no `:focus-visible` anywhere; a keyboard or switch user saw no focus at all. One outline treatment now covers every control.
- Tap targets under 44px on the bar buttons and list rows. All controls are now at least 44px, most 48px.
- `-webkit-tap-highlight-color: transparent` with nothing in its place, so taps gave no feedback. Hover and active states added; `touch-action: manipulation` removes the double-tap delay.
- No `env(safe-area-inset-*)`, so the top bar sat under the notch and the footer under the home indicator. Both inset now; the absolutely positioned footer is gone.
- No `theme-color` or `color-scheme`; Safari drew its chrome in the wrong colour. Both set.
- Decorative lock icon exposed to screen readers. Now `aria-hidden`.
- Quiz options carried their selected state in colour alone. Now `aria-pressed`, a heavier border and bold text.
- `aria-live` missing on the status area, so results were announced to nobody. Added on the checks list and the checking state.
- Times set in old-style figures, which are proportional, so the time column did not line up. Now tabular as well as old-style.
- Empty arrays rendered as an empty bordered box. Mail, Files and the evening list now say what empty means.
- Long titles could not wrap out of a flex row. `min-width: 0` and `overflow-wrap` added.
- `toLocaleDateString('en-US', …)` hardcoded. Now `Intl.DateTimeFormat` with the device locale.
- `...` and straight quotes replaced with `…` and curly quotes.
- `transition` on colour only, and the progress bar respects `prefers-reduced-motion`.

## Visual direction

The brief asked for old money, regal, as simple as the Notes app, so the cream paper, oxblood and
brass stay. The frontend-design skill flags three habits this file had picked up that read as
machine-made rather than chosen, and those are gone:

- tracked-out ALL-CAPS gold eyebrow labels above every section, now serif italic headings on a hairline rule
- meta strings joined with middle dots (`Daniel 7 · Luke 21 · 3 articles · 15 minutes`), now written as English
- an ALL-CAPS tracked footer, removed, with the connection state moved into the bar where it is also the way into Settings

## Backend, found while reviewing

- `main.py` — `/day` imported the iCal and IMAP modules at the top of the handler, so a missing optional dependency returned 500 for the whole day plan. Imports moved inside the branches that use them.
- `main.py` — the token was compared with `==`, which leaks its length and prefix by timing. Now `secrets.compare_digest`.
- `main.py` — `update_task` applied `model_dump()`, so marking a task done blanked the note the evening check had written. Now `exclude_unset=True`.
- `main.py` — `/day` errors named environment variables that no longer exist in this design. They now say what is missing in plain words.
- `seed.py` — `/dev/seed` wrote no day plan, so Today was empty in local dev. It now seeds one and clears the day's recall attempts, which makes the gate testable more than once.

## iOS

- `RootView.swift` — the server field had no `keyboardType(.URL)` and the token field no autocapitalisation rules, the same phone problem as the web settings. Fixed, with the save button disabled until both fields are filled.
- **Open**: the iOS app has no equivalent of the connection checklist. It shows one `model.message` string.

## Open

- Contrast of brass (`#8a6b2c`) on cream passes AA for text at these sizes, but the hairline rules are decorative only; do not use them to carry meaning.
- No skip link. With five rows per screen it earns nothing, but add one if the screens grow.
- The reading timer runs at 60× in the preview. That is deliberate and labelled.
