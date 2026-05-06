# Week 12 — Knowledge Gap Formulation for Compounding

**Program:** TRP1 Challenge, 10 Academy    
**Week:** 12 of 12 — Research, pedagogy, and portfolio depth

---

## What this week is

Week 12 closes the gaps in the systems built in Weeks 10–11. Each day: identify one non-trivial gap in your understanding of the day's topic, sharpen it with a peer, research and write a 600–1,000 word explainer for your partner's gap, critique each other's explainers, and commit a concrete edit to existing portfolio work.

Deliverable: five pair folders, each with a published blog post and tweet thread, plus five grounding commits back into Week 10–11 artifacts.

---

## Day 1 — Inference-Time Mechanics / LLM-as-a-Judge Bias

**Topic voted by cohort:** Inference-Time Mechanics  
**Pair:** Martha Ketsela Mengistu + Rafia

| File | Description |
|---|---|
| [question.md](pair_DAY_1/question.md) | sharpened question on KV cache mechanics and prefix caching |
| [explainer.md](pair_DAY_1/explainer.md) | explainer for Rafia's question on position bias and length bias in LLM judges |
| [morning_call_summary.md](pair_DAY_1/morning_call_summary.md) | How both questions were sharpened in the morning call |
| [evening_call_summary.md](pair_DAY_1/evening_call_summary.md) | Feedback Rafia gave and revisions Martha made |
| [signoff.md](pair_DAY_1/signoff.md) | gap-closure verdict: CLOSED |
| [grounding_commit.md](pair_DAY_1/grounding_commit.md) | edit to the Tenacious-Bench v0.1 Report |
| [sources.md](pair_DAY_1/sources.md) | Canonical papers, experiment tool, and follow-on pointers |
| [thread.md](pair_DAY_1/thread.md) | 5-tweet thread (posted) |
| [position_bias_experiment.py](pair_DAY_1/position_bias_experiment.py) | Experiment code: position and length bias across 5 Tenacious-Bench tasks |
| [position_bias_results.json](pair_DAY_1/position_bias_results.json) | Raw experiment output |

**Published artifacts:**
- Blog post: [Why Your LLM Judge Gives Different Scores Depending on Prompt Order](https://medium.com/@marthaket30/why-your-llm-judge-gives-different-scores-depending-on-prompt-order-and-what-to-do-about-it-c6bf7558d41e)
- Tweet thread: [x.com/KetselaMar83919/status/2051733684152131942](https://x.com/KetselaMar83919/status/2051733684152131942)

---

## Day 2 — Agent and Tool-Use Internals

**Topic voted by cohort:** Agent and Tool-Use Internals  
**Subtopic:** How function-calling actually works at the token level; what the model is doing when it "chooses" a tool  
**Pair:** Martha Ketsela Mengistu + Ruth Solomon

| File | Description |
|---|---|
| [question.md](pair_DAY_2/question.md) | sharpened question |
| [explainer.md](pair_DAY_2/explainer.md) | explainer |
| [morning_call_summary.md](pair_DAY_2/morning_call_summary.md) | How both questions were sharpened in the morning call |
| [evening_call_summary.md](pair_DAY_2/evening_call_summary.md) | Feedback exchanged and revisions made in the evening call |
| [signoff.md](pair_DAY_2/signoff.md) | gap-closure verdict: CLOSED |
| [grounding_commit.md](pair_DAY_2/grounding_commit.md) | edit to `hubspot_mcp.py` — all four `@mcp.tool()` docstrings rewritten from human-facing to LLM-optimized descriptions with trigger conditions and exclusion clauses |
| [sources.md](pair_DAY_2/sources.md) | Canonical papers, experiment tool, and follow-on pointers |
| [thread.md](pair_DAY_2/thread.md) | 5-post thread (pending publication) |
| [tool_failure_demo.py](pair_DAY_2/tool_failure_demo.py) | Experiment code: Path 1 (API tools parameter) vs Path 2 (text injection) on Claude Sonnet 4.6 |
| [function_calling_results.json](pair_DAY_2/function_calling_results.json) | Raw API responses from both conditions — same schema, same model, same message, only delivery path changes |


**Published artifacts:**
- Blog post: pending publication
- Tweet thread: pending publication

---

## Final submission checklist

| Item | Status |
|---|---|
| pair_DAY_1 folder — all 8 required files | ✓ |
| Blog post published under own identity (Day 1) | ✓ |
| Tweet thread published under own identity (Day 1) | ✓ |
| pair_DAY_2 folder — all 8 required files | ✓ |
| Blog post published under own identity (Day 2) | pending |
| Tweet thread published under own identity (Day 2) | pending |
| pair_DAY_3 folder | pending |
| pair_DAY_4 folder | pending |
| pair_DAY_5 folder | pending |
| synthesis.md | pending |
| canonical_list.md | pending |
| portfolio_update.md | pending |
