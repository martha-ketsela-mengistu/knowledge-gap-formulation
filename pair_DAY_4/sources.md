# Sources — Day 4 Explainer

## Canonical Papers

1. **Koo, T. K., & Mae, M. Y. (2016).** A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *Journal of Chiropractic Medicine*, 15(2), 155–163.
   - The standard reference for ICC interpretation thresholds (< 0.50 = poor, 0.50–0.75 = moderate, 0.75–0.90 = good, > 0.90 = excellent). Used in the explainer for the reliability classification table.

2. **Zheng, L., Chiang, W. L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., ... & Stoica, I. (2023).** Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.
   - Section 4 covers position bias, length bias, and judge *consistency* (running the same judge twice on the same comparison pair). The canonical LLM-judge reliability paper; directly relevant to the Automaton Auditor's multi-judge architecture.

3. **Shrout, P. E., & Fleiss, J. L. (1979).** Intraclass correlations: Uses in assessing rater reliability. *Psychological Bulletin*, 86(2), 420–428.
   - Original formulations of ICC variants (1,1), (2,1), (3,1). Used to ground the ICC(1,1) formula in the explainer.

## Tool / Pattern Used

- **`reliability_demo.py`** (this repo, `pair_DAY_4/`): Python script computing descriptive stats, SD from range, rolling CI width, and SEM under varying ICC assumptions from the 15 observed Automaton Auditor scores. Produces the sample-size table embedded in the explainer.
  - Libraries: `math`, `statistics` (stdlib only — no dependencies)
  - Run: `python reliability_demo.py`
