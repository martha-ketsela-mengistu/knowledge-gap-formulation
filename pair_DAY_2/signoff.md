# Day 2 Sign-off — Agent and Tool-Use Internals

**Martha Ketsela Mengistu**  
**Topic:** Agent and Tool-Use Internals  
**Date:** 2026-05-06

---

**Gap closure status: Closed**

The peer explainer closed the things my question asked for. I now understand that a tool call is not a special model capability — it is the model assigning higher probability to a structured JSON token sequence than to free text, and the serving infrastructure intercepting that sequence and routing it to a tool executor. The parsing boundary is clear: the model generates tokens autoregressively, the runtime parses the output post-generation, and execution is entirely outside the model. The actionable connection to my docstrings (sections 6.1 and 6.6 of the explainer) was specific and immediately usable.

---
**Status: CLOSED**
