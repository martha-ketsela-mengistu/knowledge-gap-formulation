# Signoff — Day 3

**Gap closure verdict:** Closed

---

Before today I could not explain why r=16 was the right choice for my judge — I had written "standard starting point, consistent with Unsloth defaults" and treated that as a defence. I now understand two things that change how I think about the configuration.

First, fine-tuning a pretrained model is not teaching it new knowledge; it is learning a decision boundary over representations the model already has. For a binary pass/fail task, the pretrained model already encodes the relevant features (professional tone, grounding claims, signal adequacy). The LoRA adapter only needs to shift the boundary between them. That is a low-dimensional task, and r=16 provides more than enough capacity — Aghajanyan et al. (2020) found intrinsic dimensions of a few hundred for most NLP tasks; 229K trainable params at r=16 is already over-provisioned relative to the theoretical minimum.

Second, the rank controls the information bottleneck, not raw expressivity. At r=64 on 139 training pairs, the bottleneck disappears and the model memorises rather than generalises. At r=8, the subspace may be too narrow to simultaneously represent the distinct framing differences between Seg1 and Seg2. r=16 sits in the range where the bottleneck is tight enough to force generalisation but wide enough to capture the task's actual complexity.

I can now rewrite the LoRA configuration section of `methodology_rationale.md` with a principled defence rather than a restatement of defaults.
