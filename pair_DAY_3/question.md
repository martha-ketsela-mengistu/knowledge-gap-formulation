# Day 3 Question — Training and Post-Training Mechanics

**Asker:** Martha Ketsela Mengistu  
**Topic:** Training and Post-Training Mechanics  
**Subtopic:** What LoRA actually adapts; why low rank works at all; what changes at higher rank

---

## Question

My Week 11 Sales Agent Evaluation Bench includes an **ORPO-tuned LoRA adapter** for Qwen 3.5 0.5B, trained to act as a constraint judge. The LoRA configuration in my training script is:

```python
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
```

My `methodology_rationale.md` defends this configuration as:

> "LoRA rank 16: Standard starting point. Target modules: q_proj, k_proj, v_proj... Full attention + MLP, consistent with Unsloth defaults. Alpha 32: 2× rank, standard scaling. Reducible to 8 if overfitting observed."

This is not a defense — it is a restatement of defaults. If a senior engineer asked me: *"Qwen 3.5 0.5B has an embedding dimension of 1024. You are adapting it with LoRA rank 16. That means your ΔW matrix has an intrinsic rank of 16 out of a possible 1024. Why is a rank-16 update sufficient to meaningfully change the output distribution of a model with that internal dimension? And what would actually change — in the gradient update, in the expressivity of the adapter, in the training dynamics — if you moved from rank 16 to rank 8 or rank 64?"* — I could not answer.

What does the intrinsic dimensionality of fine-tuning tell us about the relationship between task complexity and required rank? Specifically: if I had run ablations at r=8 and r=64 on my 200-pair dataset, what differences in training dynamics — loss curve shape, validation loss trajectory, signs of overfitting — would I expect to see, and why?

---

## Connection to Existing Artifact

Knowing this would let me revise:

1. **[methodology_rationale.md](../../week11/sales-agent-evaluation-bench/methodology_rationale.md)** — Section: *Backbone and LoRA Configuration*. The current paragraph is: "LoRA rank 16: Standard starting point... consistent with Unsloth defaults." I would replace this with a principled defense: why rank 16 is appropriate for a binary classification task on a 0.5B model, what the rank-to-task-complexity relationship is, and what alpha=32 actually does to the effective learning rate of the adapter.

2. **[synthesis_memos/memo_orpo_simpo_preference_methods.md](../../week11/sales-agent-evaluation-bench/synthesis_memos/memo_orpo_simpo_preference_methods.md)** — The memo explains why I chose ORPO but does not explain how LoRA interacts with the ORPO loss. Understanding the ΔW = BA decomposition would let me explain whether preference-learning gradients behave differently when applied only to the low-rank adapter versus the full weight matrix.

---

## What a Satisfying Answer Looks Like

A 600–1,000 word blog post that:

1. **Shows the ΔW = BA decomposition concretely** — with actual matrix shapes for a Qwen 3.5 0.5B attention projection layer (e.g., q_proj is 1024×1024; A is 1024×16, B is 16×1024). Makes the rank constraint visible, not abstract.

2. **Explains why low rank is not "weak"** — grounds this in the intrinsic dimensionality hypothesis: that fine-tuning a pretrained model lives in a much lower-dimensional subspace than the parameter count implies. Cites the original LoRA paper (Hu et al., 2021) and ideally the Aghajanyan et al. (2020) intrinsic dimensionality paper that motivates it.

3. **Shows what changes at higher rank** — not just "more parameters." Concretely: what does the gradient update look like differently? Does higher rank always help, or does it introduce overfitting risk on small datasets like mine (~200 preference pairs)? What does the rank-vs-validation-loss curve look like empirically?

4. **Explains what alpha actually does** — alpha=32 with r=16 gives a scaling factor of alpha/r = 2.0 applied to the LoRA output. What does this scaling multiply in the forward pass? Why is alpha usually set to 2× rank, and when would you change it?
