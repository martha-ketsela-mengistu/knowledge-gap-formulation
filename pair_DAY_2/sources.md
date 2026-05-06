# Day 2 Sources — Agent and Tool-Use Internals

*Sources used in the explainer written by Martha Ketsela Mengistu for her peer's question.*

## Papers

**Willard, B. T. & Louf, R. (2023). "Efficient Guided Generation for Large Language Models." arXiv:2307.09702**
Primary source for grammar-guided constrained decoding. Formalises how finite-state machines can be used to mask invalid tokens at each decoding step, making syntactically invalid JSON outputs structurally impossible. Directly supports the explainer's treatment of constrained decoding as a decoding-choice lever.

**Qin, Y. et al. (2023). "Tool Learning with Foundation Models." arXiv:2304.08354**
Survey of tool-learning paradigms across foundation models. Establishes the taxonomy of how models are trained to produce tool calls and situates function calling within the broader landscape of model–tool interaction research.

## Documentation

**Anthropic Tool Use Documentation**
https://docs.anthropic.com/en/docs/build-with-claude/tool-use
Primary source for Path 1 serialisation format (XML-like tool description blocks in the system context) and `tool_choice` parameter semantics on the Anthropic API.

**OpenAI Function Calling Reference**
https://platform.openai.com/docs/guides/function-calling
Primary source for OpenAI-format Path 1 (JSON function definitions in a dedicated message field) and `finish_reason: tool_calls` behaviour.

## Tool / Hands-On Experiment

**`tool_failure_demo.py` + `function_calling_results.json`**
A controlled experiment comparing Path 1 (API `tools` parameter) against Path 2 (schema injected as text in system prompt) on Claude Sonnet 4.6 via OpenRouter. Same schema, same model, same user message; only the delivery path changes. Results confirm the core claim: Path 1 produces `finish_reason: tool_calls` with parseable structured arguments; Path 2 produces a malformed `<tool_call>` text block with `finish_reason: stop`. Raw API responses are stored in `function_calling_results.json`.
