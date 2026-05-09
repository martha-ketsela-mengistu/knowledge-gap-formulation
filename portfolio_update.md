# Portfolio Update — Week 12

**Martha Ketsela Mengistu** | TRP1 Challenge | 2026-05-09  
For: FDE Hiring Review

---

## What This Document Covers

During Week 12, four days of paired gap research produced four concrete edits to the Week 10 and Week 11 portfolio artifacts. Each edit replaced a design choice that was previously stated without justification with one that can be defended at the mechanism level. This document summarises those four edits, what they changed, and why the change matters for an FDE engagement.

---

## Commit 1 — KV Cache Latency Guidance (Week 10)

**File:** `week10/conversion-engine/README.md §Known Limitations §3`

**Before:** *"Thinking model latency is high at scale — EMAIL_MODEL uses qwen3-next-80b-a3b-thinking... switch to a flash model if processing batches of 10+ leads."*

**After:** Replaced with a concrete latency analysis. The 60-token static system prompt sent to every lead represents ~270 MB of KV cache per call on Qwen3-80B. Prefix caching eliminates redundant prefill for this prefix if the static portion is kept at the beginning of every call and variable enrichment data is appended strictly after it. The updated guidance names the actionable change (prompt structure), the verification method (check `x-cache` header on OpenRouter), and the condition under which switching models is actually necessary (when the static prefix is not the bottleneck).

**Why it matters for FDE:** Clients ask about latency. "Switch to a smaller model" is a workaround. "Restructure your prompt to maximise prefix cache hits and measure the reduction" is an engineering answer. An FDE who can give the second answer adds more value in a technical discovery conversation.

---

## Commit 2 — LLM-Optimized Tool Descriptions (Week 10)

**File:** `week10/conversion-engine/agent/integrations/hubspot_mcp.py`

**Before:** Four `@mcp.tool()` docstrings written as human-facing descriptions: *"Create a HubSpot contact record with ICP classification and enrichment metadata."*

**After:** All four docstrings rewritten with LLM-optimized structure: trigger condition ("Use this tool ONLY when enrichment is complete and a final ICP classification exists"), exclusion clause ("Do NOT call if the contact record has already been created this session"), precondition, and postcondition.

**Why it matters for FDE:** A tool description that says what a tool does does not tell a model when its current reasoning state warrants calling it. Trigger conditions and exclusion clauses give the model the information it needs to distinguish "call the tool now" from "do not call yet." Any FDE building or auditing an agent tool library will encounter this problem — the fix is the same regardless of the tool domain, and the explanation is now in the codebase as a worked example.

---

## Commit 3 — LoRA Configuration Rationale (Week 11)

**File:** `week11/sales-agent-evaluation-bench/methodology_rationale.md §Backbone and LoRA Configuration`

**Before:** Three rationale cells reading "Standard starting point," "2× rank — standard scaling," and "consistent with Unsloth defaults."

**After:** Three cells with mechanism-grounded defences. LoRA rank 16: fine-tuning a pretrained model for binary pass/fail classification requires only a low-rank update because the pretrained model already encodes the relevant features; the adapter shifts the decision boundary over existing representations. At 139 training pairs, r=64 eliminates the bottleneck that forces generalisation; r=8 may be too narrow for the two task framing variants. r=16 is the appropriate tradeoff. Alpha=32: the scaling factor alpha/r = 2.0 multiplies the BA product before addition to W₀, maintaining consistent update magnitude across rank choices (Hu et al., 2022 §4.2). Target modules: adapting MLP weights alongside attention projections is required for a judging task that needs a new decision boundary, not a stylistic shift.

**Why it matters for FDE:** Clients evaluating a custom judge ask "why did you choose this configuration?" A methodology document that says "standard defaults" gives them no confidence in the system. One that explains the tradeoff between rank, dataset size, and task complexity shows that the configuration was chosen, not guessed.

---

## Commit 4 — Paired Bootstrap Mechanism (Week 11)

**File:** `week11/sales-agent-evaluation-bench/methodology_rationale.md §Expected Outcomes — Delta A`

**Before:** *"p < 0.05 on paired bootstrap (2,000 resamples)."* — the method was named, the justification absent.

**After:** A paragraph added below the target line explains the mechanism: `Var(delta_paired) = Var(A) + Var(B) − 2·Cov(A,B)`. The paired bootstrap subtracts the `2·Cov(A,B)` term that an unpaired bootstrap cannot see. In a benchmark where task difficulty is driven by prospect signal quality, both models tend to succeed and fail on the same tasks, creating high covariance. At task-level correlation ~0.97 across 59 tasks, pairing reduces CI width by ~85% vs unpaired. Without pairing, the 3 pp Delta A target is statistically undetectable at n=59.

**Why it matters for FDE:** Statistical claims in benchmark reports get challenged. "p < 0.05" is not a defence. A paragraph that names the variance source, quantifies the reduction, and shows why the effect size is detectable under the paired test — and not under the unpaired test — is a defence. This is the difference between a benchmark that a client's data scientist accepts and one they push back on.

---

## What the Four Commits Have in Common

All four edits operate at the same layer: the rationale for a design choice, not the implementation of it. The systems worked before Week 12. The gap was that the documentation described *what* the systems do without explaining *why* they are structured the way they are. An FDE who can only explain what their system does cannot defend it under technical scrutiny or adapt it to a new client context. An FDE who can explain the mechanism can do both.

The four commits cover inference-time mechanics (KV cache), agent tool-use (function-calling), post-training (LoRA rank), and evaluation statistics (bootstrap CI). Together they touch every layer of the Week 10–11 stack: the serving infrastructure, the agent orchestrator, the adapter training configuration, and the statistical test that validates the result. A hiring manager reviewing this portfolio sees a practitioner who built working systems and then understood them.
