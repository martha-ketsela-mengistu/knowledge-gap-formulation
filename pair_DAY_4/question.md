# Day 4 Question — Evaluation and Statistics

**Sharpened Question:**
In my Week 11 Sales Agent Evaluation Bench (`run_ablations.py`), I implemented a **paired bootstrap** to calculate the 95% confidence interval for my ORPO judge's detection rate (Delta A). What is the mathematical mechanism by which the "pairing" step reduces the variance of the estimate compared to an unpaired bootstrap, and why is this reduction critical for detecting small performance lifts (like my 3 pp Delta A target) in agent benchmarks with high task-level difficulty variance?

**Grounded in:**
`g:/projects/week11/sales-agent-evaluation-bench/ablations/run_ablations.py:77-96`
`g:/projects/week11/sales-agent-evaluation-bench/methodology_rationale.md:102-103`

**Connection to my work:**
Knowing this mechanism will allow me to defend the statistical significance of my ORPO judge's 3 pp improvement over the Claude baseline. Without it, my "p < 0.05" claim is a citation-shaped phrase that I cannot explain if challenged by a senior evaluator.
