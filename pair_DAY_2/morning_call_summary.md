# Day 2 Morning Call Summary

**Confirmed by:** both partners

My original question asked broadly why the LLM never invokes my MCP tools, without specifying whether I was asking about the token mechanism, the schema delivery path, or the parsing step. The call sharpened it to three named sub-questions: what token sequence represents a tool call, how tool schemas reach the model’s context, and where the boundary between model output and system parsing sits. The artifact pointer was made explicit — the gap lands on `hubspot_mcp.py` docstrings and the orchestrator comment block in `conversion_engine.py`.

My peer’s original question named the symptom (natural language output despite schemas in the prompt) but didn’t name the mechanism or the axes of failure. The call sharpened it to three axes the answer must cover: the inference-time mechanism governing the shift from free text to structured output, and how prompt design, schema specification, and decoding choices each contribute to systematic omission or invalid outputs. The artifact pointer was anchored to the specific MCP client in the Week 10 sales agent.
