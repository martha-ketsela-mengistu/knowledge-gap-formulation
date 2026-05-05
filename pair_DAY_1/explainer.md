# Why Your LLM Judge Gives Different Scores Depending on Prompt Order (And What to Do About It)

---

If you've ever used an LLM to evaluate another LLM's output — as a grader, a rubric scorer, or a pass/fail filter — you probably trust that the scores are stable. Same input, same rubric, same output = same score. Right?

**Wrong.** I ran an experiment today that broke that assumption, and the reason it breaks is in the math.

## The Setup

I'm building [Tenacious-Bench](https://github.com/martha-ketsela-mengistu/sales-agent-evaluation-bench), an evaluation benchmark for B2B sales agent outputs. The pipeline uses an LLM judge to score agent-generated emails on five rubric dimensions: tone adherence, signal grounding, bench honesty, ICP accuracy, and completeness. Each dimension gets a 1–5 score.

The judge prompt follows a standard layout:

```
INPUT CONTEXT: [prospect brief, bench capacity]
GROUND TRUTH: [banned phrases, required phrases]
AGENT OUTPUT: [the email to evaluate]
RUBRIC: [five dimensions with criteria]
```

I wanted to test a simple question: **does the order of these sections matter?**

## The Experiment

I took 5 failing tasks from my dev partition — emails that violate capacity constraints, fabricate signals, or use banned phrases. For each task, I ran the judge under three conditions:

- **Normal order**: Context → Ground Truth → Output → Rubric
- **Swapped order**: Output → Rubric → Context → Ground Truth
- **Padded output**: Same as normal, but with 60 words of generic corporate filler appended to the agent output

I compared two models: DeepSeek Chat (a generic, general-purpose model) and Claude Sonnet 4.6 (our production judge).

## The Results

| Model | Dimension Scores Changed on Position Swap | Dimension Scores Changed on Length Padding |
|---|---|---|
| DeepSeek (generic) | **52% (13/25)** | **24% (6/25)** |
| Claude Sonnet 4.6 | **16% (4/25)** | **16% (4/25)** |

**52% of DeepSeek's dimension scores changed just because I moved the agent output to the top of the prompt.** Importantly, the direction was not consistent: some tasks scored higher on swap (TEN-TR-043: `signal_grounding` 1→3, `bench_honesty` 3→4), while one task scored *lower* (TEN-TR-006: `bench_honesty` 5→3, `completeness` 5→4). In TEN-TR-006's case the normal-order condition had incorrectly given a failing email a 5 on `bench_honesty` — swapping order accidentally produced a more accurate score. That is not a success story. A judge that requires a specific prompt layout to produce a correct answer is not a reliable judge.

Even Claude wasn't immune: 16% of its scores shifted on position swap.

## Why This Happens: Token-Level Probability Mechanics

This isn't a bug — it's arithmetic.

When `deepseek-chat` scores a rubric dimension, the model isn't reasoning through the rubric symbolically. It is computing a **next-token probability distribution** over its vocabulary at the judgment token position:

```
P(next_token = "5" | all prior tokens) = softmax(W_vocab · h_T)[id("5")]
```

where `h_T` is the final hidden state after processing the entire prompt through all transformer layers. The score is `argmax` over `{"1", "2", "3", "4", "5"}`. Every bias is a bias in that log-probability.

### Position Bias

Transformer self-attention is:

```
Attention(Q, K, V) = softmax(Q K^T / √d_k) · V
```

The query at the judgment token attends over all prior key vectors. Two structural effects follow:

**Attention dilution**: In the normal-order prompt, the agent output sits between a long context block and the rubric. Its per-token attention weight is diluted across hundreds of surrounding tokens. Placing the output at position 1 removes that competition — its key vectors dominate the early context window without competition from surrounding text.

**Positional encoding asymmetry**: RoPE-encoded positional encodings weight token relationships by distance. Tokens nearer the generation front receive higher query-key similarity scores at the judgment position. When the rubric sits at the end of the prompt, its constraint language is "fresher" — it contributes more to `h_T` and the model weighs it more heavily when scoring.

The net result: the hidden state `h_T`, and therefore `log P("5" | context)`, is different for the two orderings even though the underlying content is identical.

To observe this directly, add `"logprobs": true` to your OpenRouter request and inspect the log-probability of each score token at generation time. A stable judge would show near-identical log-probability distributions for both orderings; a position-biased judge will show distributions that shift by 0.5–2.0 nats at the top score token.

### Length Bias

Length bias operates through the model's pretraining distribution. Models trained on internet text have learned that longer responses correlate with more informative content. This prior is encoded in the weight matrices that project the residual stream into vocabulary logits.

A longer response gives the model more tokens to process on the way to `h_T`, and more surface area for quality-correlated n-grams ("delivering value," "strategic alignment," "ensuring excellence") to activate features that push the vocabulary projection toward high-score tokens. In our experiment, adding 60 words of content-free filler changed 24% of DeepSeek's scores. A judge whose output changes when meaning-free tokens are appended is not evaluating constraint compliance — it is evaluating text surface features.

## The Fix: Preference-Tuned Training

The correct fix is not a better system prompt. Prompting a biased model to "ignore length" leaves the same weight matrices in place; the instruction competes with but cannot override the pretrained prior at inference time.

The fix is **domain-specific preference training** with ORPO (Monolithic Preference Optimization without Reference Model). For Tenacious-Bench, I trained a LoRA adapter on Qwen 3.5 using explicit preference pairs:

- **Chosen**: short (40-word), rubric-compliant email → high score
- **Rejected**: long (120-word), rubric-violating email → low score

LoRA trains a low-rank decomposition of the weight-update matrices (`ΔW = BA`, where `B ∈ ℝ^{d×r}`, `A ∈ ℝ^{r×k}`, rank `r ≪ d`). The ORPO loss penalizes the model for assigning higher log-probability to the rejected output than the chosen output. After training, the vocabulary projection weights have been updated so that:

```
log P("5" | short, compliant output) > log P("5" | verbose, violating output)
```

The pretrained length prior is inverted for the specific rubric. Position sensitivity is not fully eliminated — that is architectural — but combining a trained judge with position-averaging (score both orderings, take the mean) reduces inconsistency to near-zero on this rubric.

## Before You Ship an LLM-as-Judge Pipeline

1. **Run the swap test.** Score the same tasks with the output at the top vs. the bottom. If scores change, your judge has position sensitivity. Look at both directions — if scores change in *either* direction, the judge is not reliable.
2. **Run the padding test.** Add content-free filler to the output. If scores change, your judge is measuring surface text features, not rubric compliance.
3. **Measure the inconsistency rate.** If more than ~20% of dimension scores shift on either test, a generic model is not reliable enough for production evaluation.
4. **Train your judge** on domain-specific preference pairs with explicit constraint-compliance labels. A LoRA adapter is sufficient; a full fine-tune is not required.

The generic model isn't broken — it's behaving exactly as its pretraining intended. For constraint evaluation, "generally helpful" isn't good enough. You need a judge whose log-probability at the score token is conditioned on your rules, not on surface text aesthetics.

---

*Experiment code and data: [position_bias_experiment.py](position_bias_experiment.py)*

*References:*
- *Zheng et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023. https://arxiv.org/abs/2306.05685*
- *Gu et al. (2024). "A Survey on LLM-as-a-Judge." arXiv:2411.15594. https://arxiv.org/abs/2411.15594*
- *Hong, Lee & Thorne (2024). "ORPO: Monolithic Preference Optimization without Reference Model." EMNLP 2024. https://arxiv.org/abs/2403.07691*
- *Kim et al. (2024). "Prometheus 2: An Open-Source Language Model Specialized in Evaluating Other Language Models." arXiv:2405.01535. https://arxiv.org/abs/2405.01535*
