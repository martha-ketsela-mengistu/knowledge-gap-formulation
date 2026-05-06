# Why Your LLM Ignores Tool Schemas — The Inference-Time Mechanism Behind Tool Omission

Your MCP tool schemas are in the prompt. The model produces natural language anyway, or something that looks like a tool call but isn't parseable. The problem is not the schemas — it is where they are. Schema presence in the prompt is not the same as schema registration through the API mechanism. Here is the exact mechanism that governs whether a model emits a valid structured tool-call sequence, why text-injected schemas produce natural language or malformed output, and three further levers that control call reliability once the wiring is correct.

## What the Model Actually Sees

Before the model generates a single output token, the tool schema must travel through one of two paths — and which path determines whether structured tool-call output is possible at all.

**Path 1: API `tools` parameter** When you pass `tools=[...]` to the provider API, the provider serialises the schema into a specific structured format the model was post-trained on. For Anthropic's API this is XML-like tool description blocks appended to the system context; for OpenAI it is JSON function definitions in a dedicated message field. The model was instruction-tuned on this exact format and responds to it with `finish_reason: "tool_calls"` and a structured argument block. The shift from free-text generation to structured output is a trained pattern-match, not a special decoding mode.

**Path 2: Text injection in the prompt** When an MCP client injects raw schema text directly into the system prompt — `"You have access to create_enriched_contact(email, company, ...)"` — the model sees tokens that describe a tool, but not tokens in the format it was post-trained to respond to with structured output. It either ignores the schema and responds conversationally (natural language), or attempts to mimic the tool-call format from memory, producing text that resembles JSON but does not parse as a `tool_calls` API response (malformed structures that look like tool calls but fail the downstream parser).

This is the root cause of the failure. Schema presence in the prompt does not equal schema registration through the API mechanism. The model's shift from free-text to structured tool-call sequences is triggered by post-training on specific serialisation formats, not by schema visibility alone.

In the experiment below, one tool schema passed via `tools=[...]` cost **780 prompt tokens** versus 225 tokens for the equivalent schema-free call — roughly 3.5× the overhead. Schema tokens compete for attention weight with every other token, which matters once the correct path is established. Once schemas are correctly wired through the API, three design levers further control whether a call is emitted on any given turn.

## Three Secondary Controls (Once Path 1 Is Established)

Once the schema is correctly registered via the API tools parameter, three design choices govern whether a call fires on any given turn.

**Schema description quality.** Human-facing docstrings (`"Create a HubSpot contact record"`) tell the model *what* the tool does; they don't tell it *when* to call it. LLM-facing descriptions need trigger conditions: `"Call this ONLY when enrichment is confirmed. Do NOT call if segment=abstain."` Preconditions let the model match its current reasoning state to the tool directly. This matters most on ambiguous inputs and multi-tool selection; on well-tuned models with an unambiguous input, the model infers context well enough to call correctly even from a weak description.

**System prompt trigger cue.** A prompt that says "call the tool — don't describe what you would do, just do it" shifts the probability distribution away from narration toward the tool-call token. This becomes decisive on agentic tasks where the model could reasonably respond with analysis instead of action, and for models without a strong action-oriented persona established in training.

**`tool_choice` parameter.** The only hard infrastructure control. `"required"` forces a structured call regardless of model judgment; `"none"` blocks calls even when the schema is correctly registered; `"auto"` lets the model decide. Note: forcing a call does not guarantee valid arguments — that is governed separately (see below).

## When the Call Fires but the Arguments Break — and How Decoding Choices Govern Both

The original question named "malformed structures" as a failure mode distinct from "no tool call at all," and identified decoding choices as a cause. Both require separate treatment.

**Schema specification and argument hallucination.** Even when `finish_reason: "tool_calls"` fires correctly, the argument JSON can fail the downstream parser:

- **Hallucinated parameter names** — the model writes `contact_email` when the schema specifies `email`
- **Wrong types** — string `"2"` for an integer field
- **Missing required fields** — the model skips `segment_confidence` if it inferred confidence from context and didn't register it as a required slot to fill

Parameter-level descriptions that state the expected format (`"0.0–1.0 float from ICP classifier"`) reduce hallucination more than type annotations alone. The model uses the description to decide what value to fill, not just what type.

**Decoding choices at the token level.** The model generates output one token at a time by sampling from a probability distribution over the full vocabulary. Three decoding choices determine whether the sampled token sequence is parseable JSON:

First, **temperature**. At temperature 0 (greedy decoding), the model always picks the highest-probability token — producing the most syntactically consistent output. As temperature rises, lower-probability tokens get sampled more often. JSON argument blocks are particularly fragile: a single unexpected token — a dropped comma, a mismatched bracket, a string value truncated mid-way — invalidates the entire structure for the downstream parser. This means even a correctly wired Path 1 call produces unparseable arguments under high-temperature sampling.

Second, **grammar-guided (constrained) decoding**. Some providers apply a JSON grammar at each decoding step. Before sampling, they compute which tokens in the vocabulary are valid continuations of the current JSON prefix and zero out all other logits. This makes it structurally impossible to sample an invalid token mid-argument: the model can only advance through states permitted by the grammar. Willard & Louf (2023) formalise this as finite-state machine–guided generation. vLLM supports it via the Outlines backend (`--guided-decoding-backend outlines`). Models served without this constraint — open-weight models via a plain vLLM server — produce malformed argument JSON at much higher rates, especially on nested schemas or long argument blocks where drift compounds across many token steps.

Third, **`tool_choice` and what it does not do**. `tool_choice: "required"` forces the model to emit a tool-call token sequence rather than free text — it biases the initial generation toward the structured call format. It does not apply any constraint during argument generation. Once the model enters argument generation mode, constrained decoding (or lack thereof) is the only syntactic safeguard.

These three controls are independent and address different failure points. `tool_choice` governs whether a call fires at all. Constrained decoding governs whether the argument JSON is syntactically valid. Parameter-level descriptions govern whether the argument values are semantically correct. Fixing only one of the three leaves the other two failure modes open.

---

*Evidence: [function_calling_results.json](./function_calling_results.json) — raw API responses from both conditions. Same schema, same model, same user message; only the delivery path changes. Path 1 produces `finish_reason: tool_calls` with structured arguments. Path 2 produces natural language or a malformed text attempt.*

*References:*
- *Willard & Louf (2023). "Efficient Guided Generation for Large Language Models." arXiv:2307.09702 — the primary source for grammar-guided constrained decoding; formalises the finite-state machine approach used by Outlines/vLLM*
- *Qin et al. (2023). "Tool Learning with Foundation Models." arXiv:2304.08354 — survey of tool-learning paradigms; establishes the taxonomy of how models are trained to produce tool calls*
- *Anthropic Tool Use documentation: https://docs.anthropic.com/en/docs/build-with-claude/tool-use — primary source for Path 1 serialisation format and `tool_choice` semantics*
- *OpenAI Function Calling reference: https://platform.openai.com/docs/guides/function-calling — primary source for OpenAI-format Path 1 and `finish_reason: tool_calls` behaviour*
