# Canonical Reading List — Week 12

**Martha Ketsela Mengistu** | 10 Academy TRP1 Cohort

Annotated papers, documentation, and tools worth reading for any Forward-Deployed Engineer working on LLM evaluation, agent tool-use, or post-training. Drawn from four days of paired gap research.

---

## Evaluation and Statistics

**Zheng, L., Chiang, W. L., Sheng, Y., et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023.**
https://arxiv.org/abs/2306.05685

The canonical reference for LLM-as-judge reliability. Section 4.2 documents the flipped-context experiment (position bias: ~60–65% primacy bias in GPT-4-class models); Section 4.3 quantifies verbosity bias; Section 4.4 covers self-preference. Section 4 also addresses judge *consistency* — running the same judge twice on the same pair — which is the starting point for the ICC reliability analysis. Required reading before shipping any LLM-based evaluation pipeline.

---

**Koo, T. K., & Mae, M. Y. (2016). "A Guideline of Selecting and Reporting Intraclass Correlation Coefficients for Reliability Research." Journal of Chiropractic Medicine, 15(2), 155–163.**

The standard reference for interpreting ICC values in repeated-measurement contexts. Establishes the four-tier threshold system: ICC < 0.50 = poor; 0.50–0.75 = moderate; 0.75–0.90 = good; > 0.90 = excellent. Directly applicable to any LLM judge that produces variable scores across runs on the same input. Read alongside Shrout & Fleiss (1979) for the formula derivations.

---

**Shrout, P. E., & Fleiss, J. L. (1979). "Intraclass Correlations: Uses in Assessing Rater Reliability." Psychological Bulletin, 86(2), 420–428.**

The original ICC formulations. Defines ICC(1,1), ICC(2,1), and ICC(3,1) — single-measurement absolute agreement, single-measurement consistency, and average-measurement variants. Most LLM-judge reliability analyses need ICC(1,1). The paper also derives the SEM = SD·√(1−ICC) relationship that translates reliability into score units.

---

**Dror, R., Baumer, G., Shlain, M., & Reichart, R. (2019). "Deep Dominance — How to Properly Compare Deep Neural Models." ACL 2019.**
https://arxiv.org/abs/1811.01808

The NLP-specific case for paired significance tests in model comparisons. Argues that whenever two models are evaluated on the same test set — which is always true for benchmark comparisons — paired tests are required because unpaired tests ignore the within-task correlation structure. The paper formalises the claim that the paired bootstrap is the correct test for benchmark deltas, not a methodological nicety. Required reading for anyone claiming statistical significance on a held-out benchmark.

---

**Efron, B., & Tibshirani, R. J. (1993). An Introduction to the Bootstrap. Chapman & Hall.**

The canonical bootstrap reference. Chapter 9 covers the paired bootstrap and derives the variance reduction formula `Var(delta_paired) = Var(A) + Var(B) − 2·Cov(A,B)` directly. Chapter 14 covers bootstrap confidence intervals. Read Chapters 1–3 for foundations, 9 for paired methods, and 14 for CI construction. Non-parametric: makes no normality assumption, which matters for binary detection rates.

---

**Gu, J., et al. (2024). "A Survey on LLM-as-a-Judge." arXiv:2411.15594.**
https://arxiv.org/abs/2411.15594

Comprehensive taxonomy of all known LLM-as-judge biases: position, length, self-preference, verbosity, anchoring, and more. Good starting point for systematic mitigation — each bias section includes detection methodology and mitigation strategies. Use as a checklist when auditing a new judge pipeline.

---

## Training and Post-Training

**Hu, E. J., Shen, Y., Wallis, P., et al. (2022). "LoRA: Low-Rank Adaptation of Large Language Models." ICLR 2022.**
https://arxiv.org/abs/2106.09685

The LoRA paper. Section 4.2 explains what the scaling factor alpha/r does in the forward pass (multiplicative scaling of BA before addition to W₀). Section 7 covers ablations on rank — showing that r=4 is sufficient for many tasks, which is the empirical grounding for the intrinsic dimensionality claim. The rank-vs-validation-loss curves here are the reference for choosing rank on a new task.

---

**Aghajanyan, A., Zettlemoyer, L., & Gupta, S. (2020). "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning." EMNLP 2021.**
https://arxiv.org/abs/2012.13255

The theoretical basis for why LoRA works. Shows that the gradient updates needed to fine-tune a pretrained model for a specific task occupy a much lower-dimensional subspace than the full parameter count. Measures this "intrinsic dimension" for common NLP tasks (typically a few hundred dimensions). Directly explains why a rank-16 adapter is sufficient for a binary classification task on a 1024-dimensional model: the adapter rank only needs to cover the intrinsic dimension of the fine-tuning objective, not the model's embedding space.

---

**Hong, S., Lee, S., & Thorne, J. (2024). "ORPO: Monolithic Preference Optimization without Reference Model." EMNLP 2024.**
https://arxiv.org/abs/2403.07691

The ORPO training method used in the Tenacious-Bench judge. The key innovation: integrates the preference objective directly into the standard cross-entropy loss using an odds-ratio penalty, eliminating the need for a separately trained reference model. Section 3 proves the objective penalises rejected output log-probability without requiring a reference model. Required reading for any post-training that needs to run efficiently on a small model without the memory overhead of a reference model copy.

---

**Rafailov, R., Sharma, A., Mitchell, E., et al. (2023). "Direct Preference Optimization: Your Language Model is Secretly a Reward Model." NeurIPS 2023.**
https://arxiv.org/abs/2305.18290

The DPO paper. Section 3.1 derives the closed-form optimal policy from the KL-penalised RLHF objective and shows how beta enters the loss as the KL penalty coefficient. Section 4 covers the beta hyperparameter empirically: low beta allows larger updates but risks reward hacking; high beta is conservative and stable. The starting point for understanding any preference-based fine-tuning method including ORPO, SimPO, and IPO.

---

**Kim, S., et al. (2024). "Prometheus 2: An Open-Source Language Model Specialized in Evaluating Other Language Models." arXiv:2405.01535.**
https://arxiv.org/abs/2405.01535

A production-scale trained judge. Shows what a domain-specific judge training pipeline looks like: preference data construction, training procedure, and evaluation against MT-Bench baselines. Useful reference for the decision of when to train a custom judge vs use a general-purpose model.

---

## Agent Tool-Use and Function Calling

**Willard, B. T., & Louf, R. (2023). "Efficient Guided Generation for Large Language Models." arXiv:2307.09702.**
https://arxiv.org/abs/2307.09702

The constrained decoding paper. Formalises how finite-state machines can mask invalid vocabulary tokens at each decoding step, making syntactically invalid JSON outputs structurally impossible. This is what makes API tool-call Path 1 reliable: the serving infrastructure applies token masking at generation time, not post-hoc parsing. Required reading for anyone who has seen malformed tool-call JSON in production.

---

**Qin, Y., et al. (2023). "Tool Learning with Foundation Models." arXiv:2304.08354.**
https://arxiv.org/abs/2304.08354

Survey of tool-learning paradigms across foundation models. Establishes the taxonomy of how models are trained to produce tool calls and situates function calling within the broader landscape of model–tool interaction. Distinguishes between instruction-following tool use (what API function calling does) and tool-augmented reasoning (what ReAct-style agents do). Good background reading before designing a new agent architecture.

---

**Anthropic Tool Use Documentation.**
https://docs.anthropic.com/en/docs/build-with-claude/tool-use

Primary source for Path 1 serialisation format on the Anthropic API: how tool schemas are injected as XML-like blocks before the system prompt, what `tool_choice` does, and how to parse `tool_use` content blocks. Always read the provider's documentation directly — the serialisation format differs materially between Anthropic and OpenAI, and getting it wrong produces `finish_reason: stop` instead of `finish_reason: tool_calls`.

---

## Inference-Time Mechanics

**Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). "Attention Is All You Need." NeurIPS 2017.**
https://arxiv.org/abs/1706.03762

The transformer paper. Section 3.2 defines the multi-head attention mechanism and the key-value matrix projections that the KV cache stores. Required reading to understand *why* the KV cache stores key and value vectors (not query vectors) — because query vectors are position-dependent and must be recomputed at each decode step, while key-value pairs for already-processed tokens are position-independent given a fixed sequence length.

---

## Tools

| Tool | Location | What It Does |
|------|----------|-------------|
| `position_bias_experiment.py` | `pair_DAY_1/` | Measures score change rate under prompt-order and padding conditions via OpenRouter API |
| `tool_failure_demo.py` | `pair_DAY_2/` | Compares Path 1 vs Path 2 tool delivery; saves raw API responses to `function_calling_results.json` |
| `minimal_trl.ipynb` | `pair_DAY_3/` | TRL DPOTrainer on toy preference data at three beta values; produces `beta_margins.png` and `beta_gradient_scale.png` |
| `reliability_demo.py` | `pair_DAY_4/` | Given observed scores and a target CI width, computes minimum run count for stable reporting; no dependencies |
