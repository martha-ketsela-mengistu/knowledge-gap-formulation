# Evening Call Summary — Day 4

## Feedback Samuel gave on the LLM-judge reliability explainer

Samuel's first piece of feedback was that the explainer introduced ICC without first establishing why a single score is not already a reliable number — the mechanism was explained before the problem was made concrete. He flagged: "I didn't feel the urgency until the SEM table. The opening needs to land the problem before giving me the tool." Martha moved the 2.30-point range and the stochastic-draws point to the opening paragraph before any formula appeared. Samuel also noted that the practical note on ICC requiring multiple repos was buried — he had been confused about whether he could compute ICC from the 15 single-repo runs. Martha pulled that note up to immediately follow the ICC formula so readers don't misapply the tool. Finally, Samuel asked for the `judges.py` and `justice.py` links to be real file paths rather than generic references, so the explainer connected directly to his actual codebase.

## What I revised

I restructured the opening to lead with the observable problem (2.30-point range, no error bar, single draw from a distribution) before introducing ICC. The practical limitation of ICC — needing multiple repos — was moved directly under the formula with a one-sentence explanation of what to do instead (SEM and CI estimation). The file references in the adjacent-concepts section were updated to point to the actual paths in the automation-auditor project.

## Gap verdict

Samuel signed off: CLOSED. The revised explainer gave him the two tools (ICC and SEM), their thresholds, the minimum run count (9), and the connection to temperature as the upstream variance source.
