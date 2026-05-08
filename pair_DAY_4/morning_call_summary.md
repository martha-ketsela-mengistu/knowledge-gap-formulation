# Morning Call Summary — Day 4

## What was ambiguous in the original draft questions

Samuel's original draft asked whether the Automaton Auditor's score variance was a "design flaw." The interrogation was: "Is this about why variance happens, or about how to measure and report it?" The question was sharpened from a diagnosis request to a tool-identification request — specifically naming ICC and SEM as the two statistical instruments needed.

## Final question (after sharpening)

The Automaton Auditor (automation-auditor) runs 3 LLM judges at model-default temperature and combines them through a Chief Justice synthesis. Across 15 runs on the same repo, scores ranged from 1.00 to 3.30 on a 5-point scale. What are the specific statistical tools — with their formulas and interpretation thresholds — that would let me quantify how much of that 2.30-point spread is run-to-run noise versus real signal, and how many runs would I need to report a mean score with a 95% CI no wider than ±0.5?

