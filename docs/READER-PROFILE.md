# Who the issue is written for

The morning issue is written for one reader. Pitched wrong it is either patronising or useless,
and the most common failure is explaining something he has known for two years. This is the brief
the automation writes against.

**A note on what is deliberately not here.** This file records *level*, not personal detail. It
names what he already understands so the writing can start above it. It does not record health
results, lab values, or anything else private; those are not needed to pitch an article and this
file is committed to a repository. Do not add them later.

## Him, in one paragraph

Computer science at RPI, AI and ML track, with minors in information technology and economics,
graduating December 2027. Interned at GE Vernova in source-to-pay procurement, working on
AI adoption inside the business rather than as an ML engineer. Heading for product management.
Builds constantly and ships: a sensor system that won Best Hack at HackRPI, a Reddit early-signal
classifier, this app. Relearning to code unassisted after about a year of working through Claude,
specifically so he can check what AI writes for him.

## Artificial intelligence and software: where he actually is

**Assume he has:**
- Classical learning theory from Abu-Mostafa's *Learning from Data*: hypothesis sets, VC dimension,
  bias and variance, regularisation, the perceptron, why generalisation is the hard part.
- Working logistic regression, feature engineering, train and test discipline.
- Real systems ability: Python, FastAPI, MongoDB, Railway, GitHub Actions, SwiftUI, MCP
  connectors and scheduled agents. He debugs his own deploys.
- A builder's instinct for where a system will break.

**Do not explain:** what a neural network is, what training and inference are, what an API is,
what a transformer is for, what fine-tuning means, what a vector database does. He will stop
reading.

**Pitch here instead,** the layer under the headline:
- What a new model actually changed in its architecture or training, not its benchmark scores.
- Mechanism: how KV caching works and what it costs, why mixture-of-experts routing saves compute
  and where it fails, what quantisation gives up, how speculative decoding earns its speedup,
  what context length is actually limited by.
- The economics underneath: why inference pricing moves, what makes a startup's margin real or
  fake, which moats are genuine.
- Evaluation: why a benchmark number is or is not trustworthy, what contamination looks like.

He is newer to modern LLM internals than to classical ML, so attention mechanics, training
pipelines and serving architecture are fair game to teach properly. Teach them at the level of
someone who will implement a version of it, not someone who wants the gist.

**What he asked for, in his words:** the newest AI models, up-and-coming startups, tech news that
makes him smarter, or something that teaches him how to do a thing. Not Fed rates. Not macro.

## Fitness and nutrition: well past the basics

**Assume he has:** natural bodybuilding experience, a considered supplement regimen he arrived at
himself, protein-per-dollar thinking about food, familiarity with the common compounds and their
usual doses, and the habit of reading evidence rather than claims. He prefers a direct
recommendation and an honest assessment of the evidence to a list of options.

**Do not explain:** that protein matters, that creatine is well evidenced and safe, that sleep
affects recovery, that progressive overload exists, what a macro is.

**Pitch here instead:** dose-response where the curve actually bends, timing that turns out to
matter or not, what a recent trial changed about a settled belief, absorption and bioavailability
differences between forms, where the evidence is thinner than the marketing, and interactions
worth knowing. Name the study and its size. Say what it does not show.

Keep this one short. It is the second article and he asked for it brief.

## How to write for him

- Teach one thing properly rather than surveying five.
- Concrete worked examples with real numbers beat abstractions. This is a stated preference and a
  recurring complaint: explanations without context do not land.
- Plain first-person-adjacent prose. No hype, no throat-clearing, no restating the question.
- Name sources. Give the number. Say what the finding does not establish.
- A diagram when the thing is spatial, sequential or architectural. See the `svg` field on an
  article: a labelled drawing of how requests flow through a cache beats three paragraphs about it.
