# Tweet Thread — Day 4: Reliability of LLM-Judge Scoring Systems

---

**Tweet 1**

The Automaton Auditor runs 3 LLM judges (Prosecutor, Defense, Tech Lead) and outputs "Overall score 3.00/5."

15 runs on the same repo → scores ranging from 1.00 to 3.30.

Range: 2.30 points. No error bar. No run count in the report.

A single LLM-judge score is not a measurement — it is one draw from a distribution.

---

**Tweet 2**

Tool 1: **Intraclass Correlation Coefficient (ICC)**

```
ICC = (MSB - MSW) / (MSB + (k-1) * MSW)
```

MSB = variance between repos (real signal)
MSW = variance within the same repo across runs (noise)

When run-to-run noise dominates, ICC → 0.

Koo & Mae (2016): ICC < 0.50 = poor reliability. Don't use a system below this threshold for ranking.

---

**Tweet 3**

Tool 2: **Standard Error of Measurement**

```
SEM = SD * sqrt(1 - ICC)
```

From the 15 observed runs: SD = 0.611

| ICC  | SEM   | What "3.00/5" really means |
|------|-------|---------------------------|
| 0.00 | 0.611 | true value: 2.39 – 3.61  |
| 0.50 | 0.432 | true value: 2.57 – 3.43  |
| 0.90 | 0.193 | true value: 2.81 – 3.19  |

A 2.30-point range across 15 runs implies ICC is near 0. Every reported score is ±0.61 of noise.

---

**Tweet 4**

How many runs for a stable mean (±0.5 at 95% confidence)?

Estimate SD from range: 2.30 / 3.47 = 0.663 (actual sample SD: 0.611)
Solve: t(n-1) * SD / sqrt(n) <= 0.5

```
n= 7  CI=±0.565  no
n= 8  CI=±0.511  no
n= 9  CI=±0.469  YES  <-- minimum
n=12  CI=±0.388  comfortable
n=15  CI=±0.338  current data, if averaged
```

Answer: **9 runs.** The 15 already collected are enough — the problem is they were never aggregated and reported as a mean ± CI.

---

**Tweet 5**

Two things worth separating:

**Temperature is the variance source.** The Automaton Auditor's judges run at model default temperature (~0.7) with no explicit lock. Three independent stochastic draws feed into Chief Justice synthesis. The deterministic rules (weighting, override caps) apply after the draws — they can't fix upstream variance.

**Reliability ≠ Validity.** ICC measures consistency, not correctness. A reliably wrong judge has ICC=1.00 and tells you nothing true about the repo.

---

**Tweet 6**

The fix:

1. Run at least 9 times before reporting a score
2. Report "2.30 ± 0.47 (9 runs, 95% CI)" not "2.30/5"
3. Set `temperature=0` in judges.py — or document the chosen value
4. Compute ICC across multiple repos — if < 0.50, the ranking is noise

Sources: Koo & Mae 2016, Zheng et al. NeurIPS 2023
