# Sources — Day 1

---

## Canonical Papers (primary sources read)

**1. Zheng et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023.**  
https://arxiv.org/abs/2306.05685  
Primary empirical evidence for position bias and verbosity bias in LLM-as-a-judge settings. Section 4.2 documents the flipped-context experiment that demonstrates position bias; Section 4.3 quantifies length bias. The 10-point scale MT-Bench results showing ~60–65% primacy bias in GPT-4-class models are the canonical baseline against which our DeepSeek results (52%) are situated.

**2. Hong, Lee & Thorne (2024). "ORPO: Monolithic Preference Optimization without Reference Model." EMNLP 2024.**  
https://arxiv.org/abs/2403.07691  
Canonical source for the ORPO training method used in the Tenacious-Bench trained judge. Section 3 defines the odds-ratio preference objective and proves it penalizes the rejected output log-probability without requiring a separately trained reference model. Used to explain why the LoRA adapter inverts the length prior in the vocabulary projection weights.

---

## Tool / Pattern Used

**position_bias_experiment.py** — [source in this repo](position_bias_experiment.py)  
Ran 5 failing tasks from `tenacious_bench_v0.1/dev.jsonl` through DeepSeek Chat and Claude Sonnet 4.6 under three prompt conditions (normal order, swapped order, padded output) via the OpenRouter API. Results saved to [position_bias_results.json](position_bias_results.json). Total cost ~$0.03.

---

## Additional References (cited in blog, follow-on reading)

**Gu et al. (2024). "A Survey on LLM-as-a-Judge." arXiv:2411.15594.**  
https://arxiv.org/abs/2411.15594  
Comprehensive taxonomy of all known LLM-as-a-judge biases including position, length, self-preference, and verbosity. Good follow-on for anyone who wants the full landscape beyond the two mechanisms covered in this explainer.

**Kim et al. (2024). "Prometheus 2: An Open-Source Language Model Specialized in Evaluating Other Language Models." arXiv:2405.01535.**  
https://arxiv.org/abs/2405.01535  
Production example of a trained judge that addresses generic judge limitations. Shows what a domain-specific judge training pipeline looks like at scale, including the preference data construction and evaluation against MT-Bench baselines.
