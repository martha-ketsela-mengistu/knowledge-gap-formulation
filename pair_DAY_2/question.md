# Day 2 Question — Agent and Tool-Use Internals

**Asker:** Martha Ketsela Mengistu  
**Topic:** Agent and Tool-Use Internals  
**Subtopic:** How function-calling actually works at the token level; what the model is doing when it "chooses" a tool

---

## Question

My Tenacious Conversion Engine has a [FastMCP server](../../week10/conversion-engine/agent/integrations/hubspot_mcp.py) that exposes four HubSpot tools via `@mcp.tool()` decorators:

```python
@mcp.tool()
def create_enriched_contact(email: str, firstname: str, ...) -> str:
    """Create a HubSpot contact record with ICP classification
    and enrichment metadata."""

@mcp.tool()
def log_email_sent(email: str, subject: str, body: str) -> str:
    """Log an outbound email sent to a prospect in HubSpot."""

@mcp.tool()
def log_booking_created(email: str, start_time: str) -> str:
    """Log a calendar booking on the contact's timeline."""
```

But my orchestrator ([conversion_engine.py:106-128](../../week10/conversion-engine/agent/conversion_engine.py#L106-L128)) calls these tools **directly as Python functions** — the LLM never sees the tool schema, never emits a function-call token, and never decides whether to call a tool or not:

```python
# The LLM generates email text. Then MY CODE calls the tool:
crm_result_raw = create_enriched_contact(email=prospect_email, ...)
log_email_sent(prospect_email, subject, email_html)
```

I built an MCP server with tool schemas, but the LLM never touches them. I use the term "tool-use" in my documentation but I cannot explain the mechanism. Specifically:

**When a model like Claude or GPT-4 "chooses" to call a function, what is actually happening at the token level? What token sequence does the model produce to indicate a tool call? How is the tool schema (name, parameters, types) injected into the model's context, and how does the model's output parser distinguish "I want to call function X with argument Y" from regular text generation?**

Knowing this would tell me whether my MCP tool descriptions are structured correctly for an LLM to consume (they currently have human-facing docstrings, not LLM-optimized descriptions), and whether my deterministic orchestrator is a conscious architectural choice I can defend or a workaround for not knowing how to let the model drive tool selection.

---

## Connection to Existing Artifact

Knowing this would let me revise:

1. **[hubspot_mcp.py](../../week10/conversion-engine/agent/integrations/hubspot_mcp.py)** — Rewrite the `@mcp.tool()` docstrings from human-facing descriptions ("Create a HubSpot contact record") to LLM-optimized descriptions that include preconditions, postconditions, and when-to-use guidance, so the tools are correctly structured if an LLM ever consumes the schema.

2. **[conversion_engine.py](../../week10/conversion-engine/agent/conversion_engine.py)** — Add an inline comment block (or a section in README) defending *why* the orchestrator calls tools directly rather than letting the email model choose tools. Currently this is an implicit decision. After understanding the function-calling mechanism, I could state: "Deterministic tool invocation was chosen over model-driven tool selection because [specific reason grounded in how function-calling works]."

3. **[README.md §Architecture](../../week10/conversion-engine/README.md)** — The README describes the system as a "pipeline" but uses agent-adjacent language without distinguishing between scaffolded tool execution (what I built) and model-driven tool selection (what function-calling enables). Understanding the token-level mechanism would let me make this distinction precisely.

---

## What a Satisfying Answer Looks Like

A 600–1,000 word blog post that:

1. **Shows the actual token sequence** a model produces when it "calls a function" — the special tokens, the JSON structure, the stop reason — using a concrete example (e.g., a model deciding to call `create_contact` with specific parameters).

2. **Explains how the tool schema is injected** — is it appended to the system prompt? Is it a separate message role? Does the model see it as text or as structured metadata? How does this differ across providers (OpenAI `tools` parameter vs Anthropic `tool_use` vs open models with chat templates)?

3. **Shows where the parsing boundary is** — what the model generates vs what the serving infrastructure intercepts. When the model outputs `{"name": "create_contact", "arguments": {...}}`, is it generating JSON tokens autoregressively, or is there constrained decoding that forces valid JSON?

4. **Connects to tool description quality** — why a docstring like "Create a HubSpot contact record" is insufficient for LLM tool selection, and what an LLM-optimized description looks like (with when-to-use semantics, not just what-it-does semantics).
