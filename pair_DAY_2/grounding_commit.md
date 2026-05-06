# Day 2 Grounding Commit — Architecture Rationale

**Artifact edited:** [`week10/conversion-engine/agent/integrations/hubspot_mcp.py`](../../week10/conversion-engine/agent/integrations/hubspot_mcp.py)

**What changed:** All four `@mcp.tool()` docstrings were rewritten from human-facing descriptions to LLM-optimized descriptions. Before, each docstring described what the tool does (`"Create a HubSpot contact record..."`). After, each docstring states the trigger condition ("Use this tool ONLY when..."), an exclusion clause ("Do NOT call if..."), a precondition, and a postcondition.

**Why it changed:** The peer explainer and my own research established that when a model selects a tool, it is matching its current reasoning state against the probability distribution over the vocabulary — and the tool description is the primary signal that shapes which tokens the model assigns high probability to. A description that says what a tool does does not tell the model when its current state warrants calling it. Trigger conditions and exclusion clauses give the model the information it needs to distinguish "enrichment is complete, call the tool" from "I am mid-reasoning, do not call yet." This edit makes the MCP server defensible if an LLM ever consumes it via Path 1 (API `tools` parameter), rather than only being legible to a human reading the code.
