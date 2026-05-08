# Sign-off — Day 4

**Asker:** Martha Ketsela Mengistu
**Gap verdict:** CLOSED

## What I understand now that I did not before

The `2·Cov(A,B)` term is the entire mechanism. Pairing does not make the bootstrap more accurate in some general sense — it specifically removes the variance that comes from tasks being hard or easy for *both* models simultaneously. In a sales agent benchmark where difficulty is driven by prospect signal quality (clear `bench_mismatch_route_human` vs ambiguous hiring signals), both Claude and ORPO succeed and fail on the same tasks. That shared difficulty structure creates high covariance, and the paired bootstrap cancels it out by resampling `(Claude_i, ORPO_i)` pairs rather than each model's results independently.

The concrete consequence: at task-level correlation ~0.97 across 59 tasks, paired bootstrap reduces CI width by ~85% compared to unpaired (0.051 vs 0.339). Without pairing, a 3pp Delta A target is statistically undetectable. With pairing, it is detectable if the true effect exists.

I can now defend the `p < 0.05` claim in `methodology_rationale.md` because I understand what the bootstrap is actually measuring: the distribution of deltas after task-level difficulty variance has been subtracted.

