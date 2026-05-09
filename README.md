# Week 12 — Knowledge Gap Formulation for Compounding

**Program:** TRP1 Challenge, 10 Academy  
**Trainee:** Martha Ketsela Mengistu  
**Week:** 12 of 12 — Research, pedagogy, and portfolio depth

---

## What this week is

Week 12 closes the gaps in the systems built in Weeks 10–11. Each day: identify one non-trivial gap in your understanding of the day's topic, sharpen it with a peer, research and write a 600–1,000 word explainer for your partner's gap, critique each other's explainers, and commit a concrete edit to existing portfolio work.

By Day 4: eight gaps closed (four named, four researched), four blog posts and four tweet threads published under own identity, four grounding commits back into Week 10–11 artifacts.

---

## Public Artifacts

| Day | Blog Post | Tweet Thread |
|-----|-----------|-------------|
| 1 | [Why Your LLM Judge Gives Different Scores Depending on Prompt Order](https://medium.com/@marthaket30/why-your-llm-judge-gives-different-scores-depending-on-prompt-order-and-what-to-do-about-it-c6bf7558d41e) | [Thread](https://x.com/KetselaMar83919/status/2051733684152131942) |
| 2 | [Why Your LLM Ignores Tool Schemas: The Inference-Time Mechanism Behind Tool Omission](https://medium.com/@marthaket30/why-your-llm-ignores-tool-schemas-the-inference-time-mechanism-behind-tool-omission-61a8007b3445) | [Thread](https://x.com/KetselaMar83919/status/2053115720003653683) |
| 3 | [What beta=0.1 Is Actually Doing in Your DPO Trainer](https://medium.com/@marthaket30/what-beta-0-1-is-actually-doing-in-your-dpo-trainer-dd447c5a737c) | [Thread](https://x.com/KetselaMar83919/status/2053120481771884735) |

---

## Day 1 — Inference-Time Mechanics / LLM-as-a-Judge Bias

**Topic voted by cohort:** Inference-Time Mechanics  
**Pair:** Martha Ketsela Mengistu + Rafia

**Martha's gap:** KV cache mechanics and prefix caching — does a single changed token destroy the entire cached prefix, and does OpenRouter expose cache-hit state?  
**Martha's explainer for Rafia:** Why LLM judges give different scores depending on prompt order — the `argmax softmax(W_vocab · h_T)` mechanism behind position and verbosity bias.

| File | Description |
|------|-------------|
| [question.md](pair_DAY_1/question.md) | Sharpened question on KV cache mechanics and prefix caching |
| [explainer.md](pair_DAY_1/explainer.md) | Explainer for Rafia's question: position bias and length bias in LLM judges |
| [morning_call_summary.md](pair_DAY_1/morning_call_summary.md) | How both questions were sharpened in the morning call |
| [evening_call_summary.md](pair_DAY_1/evening_call_summary.md) | Feedback exchanged and revisions made in the evening call |
| [signoff.md](pair_DAY_1/signoff.md) | Gap-closure verdict: **CLOSED** |
| [grounding_commit.md](pair_DAY_1/grounding_commit.md) | Edit to the Tenacious-Bench v0.1 report — vocabulary projection language added to judge model rationale |
| [sources.md](pair_DAY_1/sources.md) | Zheng et al. 2023, Hong et al. 2024 (ORPO), plus follow-on pointers |
| [thread.md](pair_DAY_1/thread.md) | 5-tweet thread |
| [position_bias_experiment.py](pair_DAY_1/position_bias_experiment.py) | Experiment: position and padding bias across 5 Tenacious-Bench tasks via OpenRouter |
| [position_bias_results.json](pair_DAY_1/position_bias_results.json) | Raw experiment output — 52% score change rate on order swap |

**Published:**
- Blog: [Why Your LLM Judge Gives Different Scores Depending on Prompt Order](https://medium.com/@marthaket30/why-your-llm-judge-gives-different-scores-depending-on-prompt-order-and-what-to-do-about-it-c6bf7558d41e)
- Thread: [x.com/KetselaMar83919/status/2051733684152131942](https://x.com/KetselaMar83919/status/2051733684152131942)

---

## Day 2 — Agent and Tool-Use Internals

**Topic voted by cohort:** Agent and Tool-Use Internals  
**Pair:** Martha Ketsela Mengistu + Ruth Solomon

**Martha's gap:** What token sequence does the model produce when it "chooses" a tool? How does the tool schema reach the model, and where is the parsing boundary between model output and serving infrastructure?  
**Martha's explainer for Ruth:** Why LLM tool schemas injected as text (Path 2) fail where API `tools` parameter (Path 1) succeeds — constrained decoding and the `finish_reason` difference.

| File | Description |
|------|-------------|
| [question.md](pair_DAY_2/question.md) | Sharpened question on function-calling token-level mechanics |
| [explainer.md](pair_DAY_2/explainer.md) | Explainer for Ruth's question: tool schema injection paths and constrained decoding |
| [morning_call_summary.md](pair_DAY_2/morning_call_summary.md) | How both questions were sharpened in the morning call |
| [evening_call_summary.md](pair_DAY_2/evening_call_summary.md) | Feedback exchanged and revisions made |
| [signoff.md](pair_DAY_2/signoff.md) | Gap-closure verdict: **CLOSED** |
| [grounding_commit.md](pair_DAY_2/grounding_commit.md) | Edit to `hubspot_mcp.py` — all four `@mcp.tool()` docstrings rewritten from human-facing to LLM-optimized descriptions with trigger conditions and exclusion clauses |
| [sources.md](pair_DAY_2/sources.md) | Willard & Louf 2023, Qin et al. 2023, Anthropic and OpenAI documentation |
| [thread.md](pair_DAY_2/thread.md) | 5-tweet thread |
| [tool_failure_demo.py](pair_DAY_2/tool_failure_demo.py) | Experiment: Path 1 vs Path 2 tool delivery on Claude Sonnet 4.6 via OpenRouter |
| [function_calling_results.json](pair_DAY_2/function_calling_results.json) | Raw API responses — same schema, same model, only delivery path changes |

**Published:**
- Blog: [Why Your LLM Ignores Tool Schemas: The Inference-Time Mechanism Behind Tool Omission](https://medium.com/@marthaket30/why-your-llm-ignores-tool-schemas-the-inference-time-mechanism-behind-tool-omission-61a8007b3445)
- Thread: [x.com/KetselaMar83919/status/2053115720003653683](https://x.com/KetselaMar83919/status/2053115720003653683)

---

## Day 3 — Training and Post-Training Mechanics

**Topic voted by cohort:** Training and Post-Training Mechanics  
**Pair:** Martha Ketsela Mengistu + Lidya

**Martha's gap:** Why is LoRA rank 16 sufficient for a model with a 1024-dimensional embedding space? What is the relationship between intrinsic dimensionality, task complexity, and required rank?  
**Martha's explainer for Lidya:** What the DPO beta parameter actually controls — how the KL penalty coefficient survives from the RLHF objective into the DPO loss, and what happens to margins and gradients at β = 0.01, 0.1, and 0.5.

| File | Description |
|------|-------------|
| [question.md](pair_DAY_3/question.md) | Sharpened question on LoRA rank and intrinsic dimensionality |
| [explainer.md](pair_DAY_3/explainer.md) | Explainer for Lidya's question: the DPO beta parameter |
| [morning_call_summary.md](pair_DAY_3/morning_call_summary.md) | How both questions were sharpened |
| [evening_call_summary.md](pair_DAY_3/evening_call_summary.md) | Feedback and revisions |
| [signoff.md](pair_DAY_3/signoff.md) | Gap-closure verdict: **CLOSED** |
| [grounding_commit.md](pair_DAY_3/grounding_commit.md) | Edit to `methodology_rationale.md §Backbone and LoRA Configuration` — three rationale cells rewritten from "standard defaults" to mechanism-grounded defences |
| [sources.md](pair_DAY_3/sources.md) | Rafailov et al. 2023 (DPO), Stiennon et al. 2020 (RLHF) |
| [thread.md](pair_DAY_3/thread.md) | 5-tweet thread |
| [minimal_trl.ipynb](pair_DAY_3/minimal_trl.ipynb) | TRL DPOTrainer on toy preference data at β = 0.01, 0.1, 0.5 |
| [beta_margins.png](pair_DAY_3/beta_margins.png) | Margin distributions across beta values |
| [beta_gradient_scale.png](pair_DAY_3/beta_gradient_scale.png) | Gradient scale comparison across beta values |

**Published:**
- Blog: [What beta=0.1 Is Actually Doing in Your DPO Trainer](https://medium.com/@marthaket30/what-beta-0-1-is-actually-doing-in-your-dpo-trainer-dd447c5a737c)
- Thread: [x.com/KetselaMar83919/status/2053120481771884735](https://x.com/KetselaMar83919/status/2053120481771884735)

---

## Day 4 — Evaluation and Statistics

**Topic voted by cohort:** Evaluation and Statistics  
**Pair:** Martha Ketsela Mengistu + Samuel

**Martha's gap:** What is the mathematical mechanism by which the "pairing" step in a paired bootstrap reduces variance compared to an unpaired bootstrap, and why is this critical for detecting a 3 pp Delta A lift at n=59 tasks?  
**Martha's explainer for Samuel:** How to quantify reliability in an LLM-judge scoring system — ICC, SEM, and how many runs are needed to report a stable mean score within ±0.5 points at 95% confidence.

| File | Description |
|------|-------------|
| [question.md](pair_DAY_4/question.md) | Sharpened question on paired bootstrap variance reduction |
| [explainer.md](pair_DAY_4/explainer.md) | Explainer for Samuel's question: ICC, SEM, and run-count requirements |
| [morning_call_summary.md](pair_DAY_4/morning_call_summary.md) | How both questions were sharpened |
| [evening_call_summary.md](pair_DAY_4/evening_call_summary.md) | Feedback and revisions |
| [signoff.md](pair_DAY_4/signoff.md) | Gap-closure verdict: **CLOSED** |
| [grounding_commit.md](pair_DAY_4/grounding_commit.md) | Edit to `methodology_rationale.md §Delta A` — paragraph added naming the `2·Cov(A,B)` mechanism and 85% CI width reduction |
| [sources.md](pair_DAY_4/sources.md) | Koo & Mae 2016 (ICC), Zheng et al. 2023, Shrout & Fleiss 1979 |
| [thread.md](pair_DAY_4/thread.md) | 6-tweet thread |
| [reliability_demo.py](pair_DAY_4/reliability_demo.py) | Script: given observed scores and a target CI width, computes minimum run count for stable reporting |
| [demo_output.txt](pair_DAY_4/demo_output.txt) | Output of reliability_demo.py on the 15 observed scores |
| [day4peer_explainer.md](pair_DAY_4/day4peer_explainer.md) | Samuel's explainer received — the paired bootstrap variance derivation |


---

## Synthesis and Portfolio Documents

| File | Description |
|------|-------------|
| [synthesis.md](synthesis.md) | Week synthesis: eight gaps closed, most surprising finding, canonical reading list |
| [canonical_list.md](canonical_list.md) | Annotated papers, documentation, and tools contributed to the cohort canon |
| [portfolio_update.md](portfolio_update.md) | One-page summary of how the four grounding commits improve the Week 10–11 portfolio, written for an FDE hiring manager |

