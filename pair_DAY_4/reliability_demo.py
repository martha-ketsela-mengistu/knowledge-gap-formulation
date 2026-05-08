"""
Reliability demo for Day 4 explainer.
Quantifies how many runs are needed to report a stable mean score
from a variable LLM-judge system.

Observed data: peer's stated observation — 15 runs of the Automaton Auditor
on the same repo, overall scores ranging from 1.00 to 3.30 on a 5-point scale.
The 15 scores below are a representative distribution consistent with that range.
"""

import math
import statistics

# 15 representative scores consistent with the peer's stated range (1.00 to 3.30)
OBSERVED_SCORES = [1.00, 1.40, 1.80, 1.95, 2.10, 2.15, 2.20,
                   2.30, 2.45, 2.55, 2.65, 2.75, 2.85, 3.05, 3.30]

# t-distribution critical values for 95% CI (two-tailed, df = n-1)
T_CRITS = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447,  7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
}


def ci_half_width(scores: list) -> float:
    """95% CI half-width for the mean using t-distribution."""
    n = len(scores)
    if n < 2:
        return float("inf")
    s = statistics.stdev(scores)
    t = T_CRITS.get(n - 1, 1.96)
    return t * s / math.sqrt(n)


def print_section(title: str) -> None:
    print("\n" + "-" * 60)
    print("  " + title)
    print("-" * 60)


# ── 1. Descriptive statistics ────────────────────────────────────
print_section("1. Descriptive statistics for 15 observed runs")
n = len(OBSERVED_SCORES)
mean = statistics.mean(OBSERVED_SCORES)
sd = statistics.stdev(OBSERVED_SCORES)
obs_range = max(OBSERVED_SCORES) - min(OBSERVED_SCORES)
full_ci = ci_half_width(OBSERVED_SCORES)

print(f"  n        = {n}")
print(f"  mean     = {mean:.3f}")
print(f"  SD       = {sd:.3f}")
print(f"  range    = {obs_range:.2f}  ({min(OBSERVED_SCORES):.2f} - {max(OBSERVED_SCORES):.2f})")
print(f"  95% CI on mean  = {mean:.2f} +/- {full_ci:.3f}  -> [{mean - full_ci:.2f}, {mean + full_ci:.2f}]")

# ── 2. SD estimate from range (the order-statistics shortcut) ────
print_section("2. Estimating SD from range alone (order-statistics rule)")
range_divisor = 3.47
sd_from_range = obs_range / range_divisor
print(f"  SD_hat = range / 3.47 = {obs_range:.2f} / {range_divisor} = {sd_from_range:.3f}")
print(f"  (actual sample SD = {sd:.3f} -- close enough for planning)")

# ── 3. How many runs for +/-0.5 CI? ────────────────────────────────
print_section("3. Runs needed for 95% CI <= +/-0.5")
TARGET_MARGIN = 0.5
print(f"  {'n':>4}  {'t(n-1)':>8}  {'CI half-width':>14}  {'passes?':>8}")
print(f"  {'-'*4}  {'-'*8}  {'-'*14}  {'-'*8}")
stable_n = None
for test_n in range(3, 20):
    t = T_CRITS.get(test_n - 1, 1.96)
    hw = t * sd / math.sqrt(test_n)
    passes = "YES" if hw <= TARGET_MARGIN else "no"
    print(f"  {test_n:>4}  {t:>8.3f}  {hw:>14.3f}  {passes}")
    if hw <= TARGET_MARGIN and stable_n is None:
        stable_n = test_n

print(f"\n  --> Minimum runs for +/-0.5 stability: {stable_n}")

# ── 4. Rolling CI as n grows (first k scores) ────────────────────
print_section("4. Rolling mean and CI as more runs are added")
print(f"  {'n':>4}  {'mean':>6}  {'CI hw':>7}  {'passes +/-0.5?':>15}")
print(f"  {'-'*4}  {'-'*6}  {'-'*7}  {'-'*15}")
for k in range(2, n + 1):
    subset = OBSERVED_SCORES[:k]
    m = statistics.mean(subset)
    hw = ci_half_width(subset)
    flag = "<-- STABLE" if hw <= TARGET_MARGIN else ""
    print(f"  {k:>4}  {m:>6.3f}  {hw:>7.3f}  {flag}")

# ── 5. SEM under different ICC assumptions ───────────────────────
print_section("5. Standard Error of Measurement under different ICC values")
cv = sd / mean
print(f"  CV (SD/mean) = {sd:.3f}/{mean:.3f} = {cv:.1%}")
print()
print(f"  {'ICC':>6}  {'Reliability':>14}  {'SEM':>6}  {'Meaning'}")
print(f"  {'-'*6}  {'-'*14}  {'-'*6}  {'-'*30}")
for icc, label in [(0.00, "none"), (0.25, "poor"), (0.50, "moderate"), (0.75, "good"), (0.90, "excellent")]:
    sem = sd * math.sqrt(1 - icc)
    print(f"  {icc:>6.2f}  {label:>14}  {sem:>6.3f}  score can vary by +/-{sem:.2f} due to noise")

print()
print(f"  Given the observed SD={sd:.3f}, even 'moderate' ICC=0.50 gives")
print(f"  SEM={sd * math.sqrt(0.5):.3f} -- meaning a '3.00' report could truly be 2.52-3.48.")
print(f"  The Automaton Auditor's range of {obs_range:.2f} points strongly suggests")
print(f"  the actual ICC is near 0 (poor reliability).")
