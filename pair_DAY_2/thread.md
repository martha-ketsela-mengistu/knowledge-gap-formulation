# Day 2 Thread — Why LLMs Ignore Tool Schemas

**Platform:** Twitter/X or LinkedIn
**Format:** 5 posts

---

### 1/5

Your MCP tool schemas are in the prompt. The model produces natural language anyway, or broken JSON.

The problem is not the schemas — it is WHERE they are. Schema presence in the prompt ≠ schema registration via the API. Here's the mechanism. 

---

### 2/5

Two paths, completely different outcomes.

Path 1 — API `tools` parameter:
Provider serialises the schema into the format the model was post-trained on → model produces `finish_reason: tool_calls` with structured JSON arguments.

Path 2 — text injection in system prompt:
Model sees the schema as arbitrary context — no trained trigger → natural language, or text that mimics a tool call but fails the parser (malformed).

Same schema. Same model. Same user message. Only the delivery path changes.

---

### 3/5

I ran the experiment: Path 1 vs Path 2 on Claude Sonnet 4.6.

Path 1 result: `finish_reason: 'tool_calls'`, structured arguments, parseable.
Path 2 result: natural language or malformed attempt — no `tool_calls` in the response at all.

The shift from free-text generation to valid structured output is a trained pattern-match triggered by the API format, not schema visibility.

---

### 4/5

Once schemas are on Path 1, three secondary controls govern reliability:

1. Description quality — "Create a record" → model infers when. "Call ONLY when enrichment confirmed" → model matches state directly. Matters most on ambiguous inputs.

2. System prompt trigger cue — "Call the tool, don't describe what you'd do" shifts probability toward action over narration.

3. `tool_choice` parameter — the only hard control. `"required"` forces a call; `"none"` blocks it even when the schema is registered.

---

### 5/5

My Conversion Engine calls HubSpot tools as plain Python functions — the LLM never sees the schemas at all. That sidesteps Path 1 vs Path 2 entirely. No tool omission, no malformed output, but no model-driven tool selection either.

Deterministic orchestration trades flexibility for reliability. It is a choice — but only one you can defend if you understand what you opted out of.

---
