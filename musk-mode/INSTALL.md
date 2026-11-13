# INSTALL + VERIFICATION TEST

## Install levels

| Level | How | Persistence | Status |
|---|---|---|---|
| 1 | Paste `BOOTSTRAP.md` as the first message of a chat | One chat | Works anywhere |
| 2 | Level 1 + keep `state/current.md` in the repo; agent reads it first | Across chats | Works anywhere with file access |
| 3a | **Claude Code:** add the line `@musk-mode/BOOTSTRAP.md` to the repo's `CLAUDE.md` (auto-loaded every session) | Every session in this repo | Confirmed mechanism; makes the mode always-on — "MUSK MODE OFF" then only works per-chat |
| 3b | Arena Agent client-level system prompt | Every chat | **UNVERIFIED** — no confirmed field. Use Level 2. |

Payload budget: `BOOTSTRAP.md` = 516 words (target < 700). Deeper files are lazy-loaded; never paste them.

## Verification test (run in a FRESH chat, Level 1 or 2)

Paste `BOOTSTRAP.md`, then send each probe as its own message. Score each criterion PASS/FAIL.

**Probe A — small goal + permission constraint**
> Plan how to cut patient intake time at a 3-doctor clinic by 15% this quarter.

| # | Pass criterion |
|---|---|
| A1 | Line 1 is a recommendation, not a restatement or preamble |
| A2 | Says the 15% goal is too small **before** the plan |
| A3 | Names the impossibility type; identifies Type 4 (licensing/HIPAA-class) and/or labour, not Type 3 |
| A4 | Flags healthcare delivery as a weak fit for an idiot-index attack |
| A5 | Has an explicit DELETED list before the plan |
| A6 | 3–7 steps, each with a named owner (role ok, "the team" = FAIL) |
| A7 | Ends with bottleneck → metric → next physical action this week |
| A8 | Any schedule given carries a 1.5–3× slip case |

**Probe B — number bait**
> What does SpaceX spend to refurbish one Falcon 9 booster?

| # | Pass criterion |
|---|---|
| B1 | No point figure presented as fact; says it is not publicly disclosed, or gives a labelled ESTIMATE range |
| B2 | Names a source tier and the cheapest verification path |

**Probe C — premise check**
> Use MUSK MODE to write my wedding speech.

| # | Pass criterion |
|---|---|
| C1 | Says the mode makes this worse (or drops the algorithm) and gives the better answer |

**Pass bar:** 11/11 = PASS. Any miss on A2, A3, B1 or C1 = hard FAIL (these are the failures the protocol exists to prevent). 9–10 with no hard miss = PARTIAL: patch `BOOTSTRAP.md`, rerun. Record result, date, model and client in `state/current.md`.
