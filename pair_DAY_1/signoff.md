# Sign-off — Day 1

**Gap closure verdict:** CLOSED

---

Before reading the explainer, I understood that generic LLM judges produce inconsistent scores, and I had observed it empirically in my own pipeline. What I did not understand was why — I was using "position bias" and "length bias" as labels for observations I could not explain below the surface. I could not say what the model was computing when it produced a score, which meant I could not say what was actually going wrong or why training a custom judge would fix it.

The explainer closed the gap in three specific ways. First, framing the judgment as a next-token probability — `argmax softmax(W_vocab · h_T)` over score tokens — made it clear that every bias is a shift in that distribution, not a reasoning failure. This gave me a precise handle: the question is no longer "why is the judge wrong" but "what changes h_T when context order changes." Second, the attention dilution and positional encoding asymmetry explanation showed the mechanism driving that shift, and the worked-example tables made the argmax flip concrete rather than abstract. Third, the LoRA section replaced my vague sense that "trained judges are better" with a specific claim: ORPO training updates the vocabulary projection weights so that log P(high score | compliant output) > log P(high score | verbose, violating output), which is precisely the inversion the custom judge needs to perform.

