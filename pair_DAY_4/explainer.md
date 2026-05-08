# A Single Score Is Not a Measurement: Quantifying Reliability in LLM-Judge Systems

*The Automaton Auditor runs three LLM judges — Prosecutor, Defense, and Tech Lead — in parallel on the same evidence, then combines their verdicts through a deterministic Chief Justice synthesis. Fifteen runs on the same repo produced overall scores ranging from 1.00 to 3.30 on a 5-point scale. Every report presents a single number. None carries an error bar.*

---

## The Problem: One Sample, Not One Measurement

When you run a deterministic calculator on an input, you get a number. When you run an LLM judge at temperature > 0, you get a *draw from a distribution*. These are not the same thing — and reporting a single draw as if it were a stable measurement is a statistical error, not an aesthetic choice.

The mechanism behind the Automaton Auditor's variance lives in [`src/nodes/judges.py`](G:/projects/automation-auditor/src/nodes/judges.py). Each judge is a `ChatOllama` call with no explicit `temperature` parameter — it runs at the model default (~0.7). Three independent stochastic draws feed into the Chief Justice's averaging logic in [`src/nodes/justice.py`](G:/projects/automation-auditor/src/nodes/justice.py). The deterministic rules (Tech Lead weighting, Fact Supremacy penalty, Security Override cap) normalize the output somewhat, but they operate *after* the stochastic draws — they cannot eliminate the variance introduced upstream.

A 2.30-point range (1.00–3.30) on a 5-point scale across 15 runs is the observable consequence. Two statistical tools name this problem precisely: **Intraclass Correlation Coefficient (ICC)** and **Standard Error of Measurement (SEM)**.

---

## Tool 1: ICC — How Much of the Variance Is Signal?

The Intraclass Correlation Coefficient measures the fraction of total score variance that is *between targets* (real differences between repos audited) rather than *within targets* (run-to-run noise on the same repo). For a system run k times on each of N repos, ICC(1,1) is:

```
ICC = (MSB - MSW) / (MSB + (k-1) * MSW)
```

MSB is between-repo variance; MSW is within-repo run-to-run variance. When MSW dominates — as a 2.30-point spread on a single target implies — ICC approaches 0.

Koo & Mae (2016) thresholds: ICC < 0.50 = poor; 0.50–0.75 = moderate; 0.75–0.90 = good; > 0.90 = excellent. Below 0.50 the system should not be used for ranking, because the rank order is more noise than signal.

*Practical note*: ICC requires multiple repos each measured multiple times. With 15 runs on one repo you can only estimate within-target noise. That is where SEM and CI estimation take over.

---

## Tool 2: SEM — Reliability in Score Units

The Standard Error of Measurement converts ICC into the units that matter — points on your scale:

```
SEM = SD_observed * sqrt(1 - ICC)
```

When ICC is near 0, SEM ≈ SD. The measurement error is nearly as large as the scores themselves.

From the 15 observed runs (SD = 0.611):

| ICC | Reliability | SEM | What "3.00/5" really means |
|-----|-------------|-----|---------------------------|
| 0.00 | none | 0.611 | true value: 2.39–3.61 |
| 0.25 | poor | 0.529 | true value: 2.47–3.53 |
| 0.50 | moderate | 0.432 | true value: 2.57–3.43 |
| 0.75 | good | 0.305 | true value: 2.70–3.31 |
| 0.90 | excellent | 0.193 | true value: 2.81–3.19 |

A 2.30-point range across 15 runs strongly implies ICC is near 0. Even under the charitable assumption of "moderate" reliability, a reported score of "3.00" could truthfully be anywhere from 2.57 to 3.43 — a range that straddles most meaningful pass/fail thresholds.

---

## The Specific Ask: How Many Runs for ±0.5 Stability?

This is a confidence interval width problem. You want the 95% CI on the mean to be ≤ ±0.5 — meaning you report "2.30 ± 0.47" and are 95% confident the true mean falls within 0.5 points.

**Step 1 — Estimate SD from the observed range.** For n=15 draws from a normal distribution, expected range ≈ 3.47 standard deviations:

```
SD_hat = range / 3.47 = 2.30 / 3.47 = 0.663
```

The actual sample SD from the 15 scores is 0.611 — close enough that the order-statistics shortcut works as a planning estimate without all the raw data.

**Step 2 — Solve for n** such that `t(n-1) * SD / sqrt(n) ≤ 0.5` (using SD = 0.611):

| n | t(n−1) | CI half-width |
|---|--------|--------------|
| 7 | 2.447 | ±0.565 — too wide |
| 8 | 2.365 | ±0.511 — too wide |
| **9** | **2.306** | **±0.469 — passes** |
| 10 | 2.262 | ±0.437 |
| 12 | 2.201 | ±0.388 |

**Answer: 9 runs minimum.** With 9 runs the 95% CI on the mean reaches ±0.47 — just inside the ±0.5 threshold. The 15 runs already collected are more than sufficient; the problem is they were never aggregated and reported as a mean with a CI.

```
# reliability_demo.py output (run on the 15 observed scores):
n=7   CI hw=0.565   no
n=8   CI hw=0.511   no
n=9   CI hw=0.469   YES  <-- minimum
n=12  CI hw=0.388   YES  <-- comfortable margin
n=15  CI hw=0.338   YES  <-- current data, if averaged
```

The full script is at [`pair_DAY_4/reliability_demo.py`](reliability_demo.py).

---

## Two Adjacent Concepts

**Temperature is the variance source.** The judges in [`judges.py`](G:/projects/automation-auditor/src/nodes/judges.py) use `ChatOllama` with no `temperature` parameter — each of the three judges draws independently at the model default. The Chief Justice averages them, which helps (averaging three draws is tighter than one), but the deterministic rules in [`justice.py`](G:/projects/automation-auditor/src/nodes/justice.py) apply *after* the stochastic draws and cannot compensate for large upstream variance. Setting `temperature=0` would eliminate stochastic variance — but may introduce a systematic bias the model would otherwise average out. Neither is free; the choice should be documented.

**Reliability is not validity.** ICC and SEM measure *consistency*, not *correctness*. A judge that reliably gives every repo a 3.00 has ICC=1.00 and tells you nothing about the repo. These tools quantify noise; a separate calibration study is required to verify the signal.

---

## Sources

- Koo, T. K., & Mae, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. *Journal of Chiropractic Medicine*, 15(2), 155–163.
- Zheng, L., Chiang, W. L., Sheng, Y., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023*. (Section 4 covers judge consistency across repeated runs.)
- Shrout, P. E., & Fleiss, J. L. (1979). Intraclass correlations: Uses in assessing rater reliability. *Psychological Bulletin*, 86(2), 420–428.
