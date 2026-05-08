# Grounding Commit — Day 4

**Artifact edited:** `G:/projects/week11/sales-agent-evaluation-bench/methodology_rationale.md`
**Section:** Statistical Test (lines 102–103)

## Before

> Delta A target: ≥3 pp lift on Tenacious-Bench held-out composite score vs Week 10 Claude-only baseline, with p < 0.05 on paired bootstrap (2 000 resamples).

## After (paragraph added below that line)

> Delta A uses a 2,000-resample paired bootstrap rather than an unpaired bootstrap because task-level difficulty variance in `tenacious_bench_v0.1` creates high covariance between the two models' per-task scores. The paired bootstrap removes this shared variance by resampling `(Claude_i, ORPO_i)` task pairs rather than resampling each model's results independently. The variance reduction is `2·Cov(A, B)`, which at observed task-level correlation of ~0.97 reduces CI width by approximately 85% compared to an unpaired bootstrap. Without pairing, the 3pp Delta A target is statistically undetectable at n=59 tasks.

## What changed and why

Before this edit, "p < 0.05 on paired bootstrap" was a citation-shaped phrase — the method was named but not defended. After, the paragraph names the mechanism (covariance cancellation), states the specific consequence (85% CI width reduction), and connects it to the benchmark's task structure (difficulty variance driven by prospect signal quality). A senior evaluator who pushes back on the statistical claim can now be shown this paragraph rather than a blank look.
