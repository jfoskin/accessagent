# Access Agent — Project Documentation

## Application Overview

**Purpose:** Access Agent automates accessibility assessment for websites, combining fast, deterministic rule-based detection with targeted LLM reasoning to produce a clear, prioritized report against WCAG 2.2.

**Problem it solves:** Automated accessibility tools catch real violations but present them as an unexplained rule dump. Mapping each violation to a WCAG criterion and understanding what to actually do about it requires expertise most developers don't have. Access Agent resolves the WCAG mapping deterministically and adds an on-demand LLM explanation for any specific finding a developer wants to understand.

**Intended users:** developers who want a usable, explained accessibility report for a URL without first becoming WCAG experts.

## Technical Workflow Diagram

User enters URL (Streamlit UI)
│
▼
Planner Node - (routes to DOM scan — single path in Phase 1)
│
▼
DOM Scan Node
(Playwright launches headless Chromium, navigates to URL,
axe-core scans the rendered page)
│
▼
Normalize to Finding schema
(Pydantic — rule_id, severity, location, raw WCAG tags;
WCAG criterion + level parsed directly from axe-core's
own tags — deterministic, no LLM involved)
│
▼
Aggregator Node
(deterministic Python dedup — same rule_id + selector
within one scanner source is the same issue; no LLM call)
│
▼
Report Node
│
▼
Streamlit UI renders severity-sorted findings
│
▼
[on user click] "Explain this issue"
│
▼
explain_finding() — Ollama, structured output,
generates why_it_matters + suggested_fix for
ONE finding, grounded in its real selector


Error handling: every stage that can fail (Playwright navigation, axe-core execution) is wrapped so failures are logged to `state.errors` and surfaced in the UI, rather than crashing the app.

## Tools, Libraries & Frameworks Used

| Tool | Role |
|---|---|
| **LangGraph** | Orchestrates the pipeline as a graph (planner → DOM scan → aggregator → report) |
| **Ollama** (`qwen3:8b`, configurable via `OLLAMA_MODEL`) | Open-source LLM powering on-demand finding explanations — no paid API |
| **Playwright** | Headless browser automation to render the target page |
| **axe-core** (via `axe-core-python`) | Automated WCAG rule engine — the detection layer, and the source of truth for WCAG criterion/level mapping |
| **Pydantic** | Schema validation (`Finding`, `AggregatedFinding`), with `extra="forbid"` to reject malformed LLM output |
| **Streamlit** | Web UI for input, results, and on-demand explanations |
| **pytest** | Automated test suite |
| **uv** | Dependency management |

*(Claude API supported as an optional alternate provider through the same `get_llm()` interface, not required for the app to run.)*

## Application Architecture

**`state.py`** — the shared data contract. `Finding` (pre-aggregation) and `AggregatedFinding` (post-aggregation, adds `is_best_practice` and `why_it_matters`) both allow `wcag_criterion`/`level` to be `None`, reflecting that not every axe-core rule maps to an actual WCAG success criterion — some are best-practice recommendations only.

**`wcag_reference.py`** — deterministic WCAG facts, resolved without any LLM involvement: `parse_wcag_from_tags()` extracts the criterion and level directly from axe-core's own rule tags (e.g. `wcag143` → `1.4.3`, `AA`); `WCAG_NAMES`/`get_name()` and `WCAG_SLUGS`/`get_reference_url()` provide the human-readable name and official W3C reference link; `is_obsolete_in_2_2()` flags criteria (currently 4.1.1) that axe-core still tags even though the W3C removed them in WCAG 2.2.

**`nodes/dom_scan.py`** — launches Playwright, runs axe-core against the rendered page, normalizes raw violations (one `Finding` per affected DOM element) using `parse_wcag_from_tags` for WCAG grounding.

**`nodes/aggregator.py`** — deterministic Python deduplication, keyed on `(rule_id, selector)`. No LLM call. This was a deliberate architecture change (see Challenges below) — with a single scanner source, deduplication is a mechanical match, not a judgment call.

**`nodes/explain.py`** — `explain_finding()`, the project's one LLM integration point. Called on demand from the UI for a single finding at a time, using `get_llm().with_structured_output(Explanation)` to generate a grounded `why_it_matters` and `suggested_fix`, referencing the finding's actual selector.

**`llm.py`** — a single `get_llm()` function returning `ChatOllama` or `ChatAnthropic` based on `LLM_PROVIDER`, so the model backend is swappable without touching any node logic.

**`graph.py`** — wires the nodes into a `StateGraph`, defining the fixed Phase-1 path.

**`app.py`** — Streamlit entry point. Persists scan results and per-finding explanations in `st.session_state` so they survive Streamlit's rerun-on-every-interaction model.

## Features & Functionality

- **URL-based scanning** — renders the page in a real browser before scanning, catching JS-rendered content static tools would miss
- **Deterministic WCAG 2.2 mapping** — criterion and level extracted directly from axe-core's own rule metadata, not LLM inference, eliminating a class of hallucination risk
- **Best-practice vs. WCAG-requirement distinction** — findings with no real WCAG mapping are labeled as best-practice recommendations rather than assigned a fabricated criterion
- **Obsolete-criterion flagging** — a finding tagged with a criterion no longer valid in WCAG 2.2 (currently 4.1.1) is explicitly marked, rather than presented as current
- **On-demand LLM explanations** — a plain-language "why it matters" and a concrete, selector-grounded suggested fix, generated only for findings a user actually wants explained
- **Fast, scalable detection** — scan and dedup no longer depend on LLM inference time, so results return quickly regardless of how many violations a page has
- **Swappable LLM backend** — Ollama (default, no paid API) or Claude (optional), controlled by one environment variable

## Challenges & Lessons Learned

- **LLM structured-output does not scale linearly with batch size.** Sending every finding from a page to the LLM in one aggregation call worked on small test fixtures (~20 findings, ~2 minutes) but hung for over 86 minutes on a real page with 111 findings. Rather than just increasing timeouts, this was resolved architecturally: WCAG mapping moved to a deterministic lookup against axe-core's own rule tags, deduplication was rewritten as plain Python, and the LLM's role was narrowed to on-demand, per-finding explanation generation. This took the worst case from an unbounded, multi-hour hang to a scan that returns in seconds, while keeping genuine LLM functionality central to the app.

- **A rule engine's own metadata can lag behind the spec it claims to reference.** Grounding WCAG mappings in axe-core's tags eliminated most hallucination, but one real gap surfaced: axe-core tags `duplicate-id-active` with WCAG criterion 4.1.1, which the W3C removed/made obsolete in WCAG 2.2. Rather than trusting the tag silently, the app now explicitly flags criteria known to be obsolete in 2.2.

- **A syntactically valid LLM response can still be practically empty.** An early version of the explanation prompt produced a technically well-formed but meaningless fix suggestion — instructing a developer to rename an ID from `button1` to `button1`. The prompt never gave the model the finding's actual CSS selector, so it fabricated a generic template with no real content. Passing the real selector into the prompt and explicitly forbidding placeholder examples produced concrete, actionable output.

- **A quiet logic bug in severity mapping** — `impact is valid` instead of `impact in valid` — caused every finding to silently default to "moderate" severity regardless of axe-core's actual rating. It passed existing tests, which checked validity but not correctness, and was only caught through deliberate manual code review — a reminder that passing tests confirm shape, not necessarily logic.

- **Streamlit's rerun model and widget identity are easy to get subtly wrong.** Results computed inside a button's `if` block vanished on the next rerun because they weren't persisted in `st.session_state`; a manually chosen session-state key collided with Streamlit's own internal button-state key under the same name; and `st.expander`'s `expanded` argument was silently ignored once a user had interacted with the page, requiring an explicit `key` to make the expander a properly controllable widget.

- **Next steps:** Phase 2 will add repo input and a Static Code Scan Agent. This is the point where LLM-based aggregation is planned to return — matching semantically equivalent findings reported by two different scanners in different vocabularies is a genuine judgment call, unlike the mechanical single-source matching used in Phase 1.