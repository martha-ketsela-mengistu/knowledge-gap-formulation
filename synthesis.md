# Week 12 Synthesis: Knowledge Gap Formulation

**Martha Ketsela Mengistu** | 10 Academy TRP1 Cohort | Week of 2026-05-05

---

## What This Week Did

Weeks 10 and 11 produced two working systems: a Tenacious Conversion Engine that researches and emails B2B leads, and a Sales Agent Evaluation Bench that trains a custom ORPO judge and measures its performance lift. Week 12 was the audit. Each day the cohort named one gap in their understanding of the engineering that underlies those systems, sent it to a peer to research and explain, received an explainer back, and committed a concrete edit to existing work. By the end of four days, the systems are the same — but the documentation is no longer aspirational. Every claim in `methodology_rationale.md`, every docstring in `hubspot_mcp.py`, and every paragraph in the bench's grounding traces can now be defended at the mechanism level.

---

## Part I — The Four Gaps I Named

### Gap 1 — KV Cache: Does a Changed Token Destroy the Whole Cache?

**Topic:** Inference-time mechanics  
**Artifact:** `conversion_engine.py:201–205` — a 60-token static system prompt sent identically to every lead

My benchmark was processing 20 leads sequentially with p50 latency of 46.6s. I knew "prefix caching" existed but could not answer three questions: what the KV cache actually stores per token, what the memory cost is on an 80B model, and whether a single changed token at position N invalidates the cache from position N onward or destroys it entirely. I could not tell whether the OpenRouter proxy was silently absorbing the redundant prefill cost or whether I was paying 20× for identical tokens.

The explainer answered all three. The KV cache stores the key and value projection vectors for each layer and each already-processed token — never the query vectors, because query depends on the current decode position. Invalidation is strictly prefix-based: any token change at position k invalidates the cache for all tokens k and later, not the whole cache. On Qwen3-80B, a single token's KV entry costs approximately 4.5 MB across all layers; the 60-token system prompt costs ~270 MB to cache — significant but well within inference memory for dedicated serving.

**What changed:** `README.md §Known Limitations §3` was updated from "switch to a flash model if processing batches of 10+ leads" to a concrete recommendation: keep the static system prompt at the beginning of every call, append variable enrichment data strictly after the fixed portion, and verify cache-hit rate via the `x-cache` response header that OpenRouter exposes on supported models.

---

### Gap 2 — Function Calling: What Token Sequence Does the Model Actually Produce?

**Topic:** Agent and tool-use internals  
**Artifact:** `hubspot_mcp.py` — four `@mcp.tool()` tools that the LLM never calls

My Tenacious Conversion Engine builds an MCP server with tool schemas but bypasses it entirely: the LLM generates email text and then Python code calls the tools directly. My documentation used the phrase "tool-use" without being able to define it. I could not explain whether my MCP tool descriptions were structured correctly for an LLM to consume, or whether my deterministic orchestrator was an architectural choice I could defend or an accident.

The explainer closed the gap precisely. A tool call is the model assigning higher probability to a structured JSON token sequence than to free text — the model outputs `{"type": "tool_use", "name": "create_contact", "input": {...}}` autoregressively, and the serving infrastructure intercepts this at the stop token and routes to the executor. The parsing boundary is outside the model. Path 1 (API `tools` parameter) and Path 2 (schema-in-system-prompt) produce different stop reasons (`tool_calls` vs `stop`) and different parsing reliability, which I confirmed experimentally with `tool_failure_demo.py`.

**What changed:** All four `@mcp.tool()` docstrings in `hubspot_mcp.py` were rewritten from human-facing descriptions ("Create a HubSpot contact record") to LLM-optimized descriptions with trigger conditions, exclusion clauses, and when-to-use semantics. The architecture section of the Week 10 README was updated to distinguish deterministic scaffolding (what I built) from model-driven tool selection (what function-calling enables) and to defend the choice.

---

### Gap 3 — LoRA Rank: Why Is Rank 16 Sufficient for a 1024-Dimensional Model?

**Topic:** Training and post-training mechanics  
**Artifact:** `methodology_rationale.md §Backbone and LoRA Configuration` — "Standard starting point; consistent with Unsloth defaults"

My LoRA configuration uses `r=16` on Qwen 3.5 0.5B (embedding dimension 1024), meaning ΔW = BA where A is 1024×16 and B is 16×1024. The methodological rationale column said "standard starting point, consistent with Unsloth defaults" — a restatement, not a defense. If a senior engineer asked why rank 16 rather than rank 8 or rank 64, I had no answer.

The explainer grounded this in the intrinsic dimensionality result (Aghajanyan et al., 2020): fine-tuning a pretrained model does not require high-dimensional weight updates because the task-relevant gradient lives in a low-dimensional subspace of the full parameter space. For a binary pass/fail classification task, the pretrained model already encodes the relevant features (professional tone, grounding claims, signal adequacy); the adapter shifts the decision boundary over existing representations rather than building new ones. At 139 training pairs, r=64 eliminates the bottleneck that forces generalisation and causes overfitting; r=8 may be too narrow to simultaneously represent both task framing variants (Seg1 vs Seg2). r=16 with alpha=32 sits at the right tradeoff.

**What changed:** `methodology_rationale.md §Backbone and LoRA Configuration` was rewritten with a principled defence: named the intrinsic dimensionality mechanism, stated the trainable parameter count (~229K at r=16), and explained what alpha/r = 2.0 does in the forward pass (scales the BA product before addition to W₀, maintaining consistent update magnitude across rank choices).

---

### Gap 4 — Paired Bootstrap: What Does the "Pairing" Actually Remove?

**Topic:** Evaluation and statistics  
**Artifact:** `run_ablations.py:77–96` — `paired_bootstrap()` computing Delta A CIs

My `paired_bootstrap()` implementation resamples `(Claude_i, ORPO_i)` task pairs and was accompanied in `methodology_rationale.md` by the phrase "p < 0.05 on paired bootstrap (2,000 resamples)" — a citation-shaped phrase I could not explain. If challenged on why paired rather than unpaired, I had no answer.

The explainer named the mechanism: `Var(delta_unpaired) = Var(A) + Var(B)`, while `Var(delta_paired) = Var(A) + Var(B) − 2·Cov(A,B)`. The `2·Cov(A,B)` subtraction is the entire point. In a sales agent benchmark where task difficulty is driven by prospect signal quality — clear `bench_mismatch_route_human` vs ambiguous hiring signals — both Claude and ORPO tend to succeed and fail on the same tasks. That shared structure creates high covariance. At task-level correlation ~0.97 across 59 tasks, pairing reduces CI width by ~85% compared to unpaired. Without pairing, a 3 pp Delta A target is statistically undetectable at n=59 tasks.

**What changed:** `methodology_rationale.md §Statistical Test` now contains a paragraph naming the mechanism, stating the variance reduction formula, and connecting it to the benchmark's task structure. The implementation in `run_ablations.py` was already correct; the documentation now defends it.

---

## Part II — The Four Gaps I Researched

### Researched 1 — Why LLM Judges Give Different Scores Depending on Prompt Order

**Topic I explained:** LLM-as-judge position bias and its mathematical mechanism  
**For:** Rafia's question about the Automaton Auditor producing inconsistent rubric scores

A generic LLM judge computes its verdict as `argmax softmax(W_vocab · h_T)` over score tokens. The hidden state `h_T` is shaped by surface features — prompt order and output length — that are independent of rubric compliance. When the judged output is presented first rather than second, attention dilution and positional encoding asymmetry shift `h_T` enough to flip the argmax. I ran a controlled experiment (`position_bias_experiment.py`) across 5 tasks and 3 prompt conditions and observed 52% of dimension scores changing on order swap. The ORPO adapter addresses this by updating the vocabulary projection weights so that `log P(high score | compliant output) > log P(high score | verbose output)`, inverting the length prior for the Tenacious-Bench rubric.

---

### Researched 2 — Tool Schema Injection and Constrained Decoding

**Topic I explained:** How tool descriptions reach the model and how JSON validity is enforced  
**For:** Ruth's question about why their MCP tool descriptions weren't being used by the LLM

The tool schema travels to the model via one of two paths: Path 1 (API `tools` parameter, serialised by the serving infrastructure as XML-like blocks before the system prompt) or Path 2 (manually injected as text). Path 1 produces a `finish_reason: tool_calls` stop condition that the client parser handles; Path 2 produces `finish_reason: stop` with embedded text the client must parse manually. Constrained decoding (Willard & Louf, 2023) can enforce valid JSON at the token level by masking vocabulary tokens that would produce syntactically invalid continuations — this is what makes Path 1 reliable and Path 2 fragile. Confirmed experimentally with `tool_failure_demo.py` and `function_calling_results.json`.

---

### Researched 3 — What the DPO Beta Parameter Actually Controls

**Topic I explained:** The role of the KL penalty coefficient in DPO and ORPO training  
**For:** Lidiya's question about why beta values produce different training dynamics

The DPO objective is derived from the KL-penalised RLHF reward: `max E[r] − β·KL(π ‖ π_ref)`. Beta survives into the DPO loss as the coefficient that controls how strongly the policy is penalised for diverging from the reference model. High beta collapses the margin between preferred and rejected log-probabilities, making training stable but conservative; low beta allows larger updates but risks reward hacking or mode collapse. I ran TRL `DPOTrainer` with GPT-2 on toy preference data at β = 0.01, 0.1, and 0.5 and showed the margin distribution and gradient scale differences concretely in `minimal_trl.ipynb`.

---

### Researched 4 — Quantifying Reliability in LLM-Judge Scoring Systems

**Topic I explained:** ICC, SEM, and sample-size requirements for stable scores  
**For:** Samuel's question about the Automaton Auditor's 2.30-point score spread across 15 runs

A single LLM-judge score is one draw from a distribution, not a measurement. The Intraclass Correlation Coefficient (ICC) quantifies the fraction of total score variance that is real signal between targets rather than run-to-run noise. When ICC is near 0, the Standard Error of Measurement (SEM = SD·√(1−ICC)) approaches the observed SD — the error is nearly as large as the scores. From the 15 observed runs (SD = 0.611, range = 2.30), the 95% CI on the mean requires 9 runs to reach ±0.5 width. The system needs to report "2.30 ± 0.47 (9 runs, 95% CI)" rather than "2.30/5." Root cause: `judges.py` uses `ChatOllama` with no explicit temperature — three independent stochastic draws feed into the Chief Justice synthesis.

---

---

## Part III — The Most Surprising Thing I Learned

The most surprising finding was in Gap 1 (KV cache), but the insight that changed how I think most broadly came from Gap 4 (paired bootstrap).

I had assumed that using a paired bootstrap was a methodological nicety — a best practice that improved precision slightly. The explainer showed it is not a nicety: it is the difference between a statistically detectable result and a null result. At n=59 tasks with the observed task-level correlation (~0.97), the unpaired CI spans 34 percentage points and includes zero; the paired CI spans 5 percentage points and excludes zero. The same data, the same delta, but only one statistical test can see the signal. The mechanism — `2·Cov(A,B)` subtraction — is simple enough to write in one line, but its practical consequence (85% CI width reduction) is large enough that not understanding it means shipping a benchmark that cannot answer its own question.

The adjacent insight: all four grounding commits this week edited `methodology_rationale.md` or `hubspot_mcp.py` — the same two files that describe design choices. This is not coincidence. The gaps that persisted into Week 12 were not in the working code; they were in the rationale for why the code is structured the way it is. Shipping a working system is necessary but not sufficient. A system whose choices you cannot defend at the mechanism level is not production-ready in the FDE sense.

---

## Part IV — Canonical Reading List

*See `canonical_list.md` for the full annotated list. Summary below.*

**Must-read for evaluation work:**
- Zheng et al. (2023), "Judging LLM-as-a-Judge" (NeurIPS) — position bias, verbosity bias, consistency
- Dror et al. (2019), "Deep Dominance" (ACL) — paired significance tests for model comparison
- Efron & Tibshirani (1993), *An Introduction to the Bootstrap* — Chapter 9 for paired bootstrap derivation
- Koo & Mae (2016), ICC guideline (J. Chiropractic Medicine) — ICC thresholds for reliability

**Must-read for training:**
- Hu et al. (2022), "LoRA" (ICLR) — the ΔW = BA decomposition and why low rank works
- Aghajanyan et al. (2020), "Intrinsic Dimensionality" (EMNLP) — the theoretical basis for LoRA
- Hong et al. (2024), "ORPO" (EMNLP) — the preference objective used in the Tenacious-Bench judge

**Must-read for tool-use and agent internals:**
- Willard & Louf (2023), "Efficient Guided Generation" (arXiv) — constrained decoding via FSMs
- Qin et al. (2023), "Tool Learning with Foundation Models" (arXiv) — tool-learning taxonomy

---

## Part V — Tool List

| Tool | Purpose | Where Used |
|------|---------|------------|
| `position_bias_experiment.py` | Measures score change rate under prompt-order and padding conditions | Day 1 — confirmed 52% inconsistency rate on DeepSeek |
| `tool_failure_demo.py` | Compares Path 1 vs Path 2 tool schema delivery on Claude Sonnet 4.6 | Day 2 — confirmed `finish_reason: tool_calls` vs `stop` difference |
| `minimal_trl.ipynb` (TRL DPOTrainer) | Trains GPT-2 on toy preference data at three beta values | Day 3 — shows margin and gradient scale effects of beta |
| `reliability_demo.py` | Computes ICC/SEM/CI width from observed score distribution | Day 4 — shows 9 runs needed for ±0.5 stability |
