# Grounding Commit — Day 3

**Artifact edited:** `g:/projects/week11/sales-agent-evaluation-bench/methodology_rationale.md`  
**Section:** Backbone and LoRA Configuration — rows: LoRA rank, LoRA alpha, Target modules

---

## What changed

The LoRA rank rationale was rewritten from "Standard starting point; reducible to 8 if overfitting" to a principled defence grounded in intrinsic dimensionality. The new rationale names the mechanism (pretrained model already encodes the relevant features; the adapter shifts the decision boundary, not the representations), gives the trainable parameter count (≈229K across 7 modules at r=16), and states why r=8 and r=64 are worse choices for this specific dataset size (139 pairs).

The LoRA alpha rationale was rewritten from "2× rank — standard scaling" to an explanation of what alpha actually does in the forward pass: the scaling factor alpha/r multiplies BA before addition to W₀, and setting alpha = 2r maintains consistent update magnitude across rank choices, following Hu et al. (2022) §4.2.

The target modules rationale was rewritten from "consistent with Unsloth defaults" to a task-motivated explanation: adapting MLP weights alongside attention projections is necessary for a judging task that requires learning a new decision boundary, not a stylistic shift.

## Why it changed

Before Day 3 I understood that these were "good defaults." After reading Lidya's explainer on intrinsic dimensionality, I understand that the choice of r=16 is not arbitrary — it reflects a claim about the complexity of the fine-tuning task relative to the model's existing representations. The previous rationale column was a restatement of tool defaults, not a defence. A reader of the methodology document could not have reconstructed why r=16 rather than r=8 or r=64; they can now.
