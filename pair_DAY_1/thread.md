# Day 1 Thread — Position Bias in LLM Judges

**Platform:** Twitter/X  
**Published at:** https://x.com/KetselaMar83919/status/2051733684152131942  
**Format:** 5 posts (each ≤ 280 characters)

---

### 1/5

Experiment: I scored 5 sales agent eval tasks, then moved the agent output to the top of the judge prompt. Not a single word changed.

52% of scores changed. Same input. Different verdict. Just from text position.

Here's what I found 🧵

---

### 2/5

The setup:
- 5 failing tasks (Tenacious-Bench)
- 3 conditions: normal, swapped, padded output
- 2 models: DeepSeek Chat vs Claude Sonnet 4.6

DeepSeek: 52% of scores changed on swap
Claude: 16% changed

The bias goes both ways — not just leniency.

---

### 3/5

Why does this happen?

Attention weights must sum to 1.0 (softmax). When the output is at the top, it holds structural prominence. Buried in the middle, its weight dilutes across hundreds of context tokens.

The model isn't wrong — its architecture makes order matter.

---

### 4/5

Length bias is real too.

I appended 60 words of filler to each output. 24% of DeepSeek's scores changed.

Trained on internet text where longer = better. Your failed email can score higher just by being more verbose.

---

### 5/5

The fix: train your judge on domain-specific preference pairs.

I trained an ORPO adapter (Qwen 3.5) on (compliant, violating) pairs. Short+correct > long+wrong.

Generic models aren't broken — just optimized for the wrong objective.

Full post + code: https://medium.com/@marthaket30/why-your-llm-judge-gives-different-scores-depending-on-prompt-order-and-what-to-do-about-it-c6bf7558d41e

---
