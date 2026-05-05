"""
Position-bias and length-bias experiment for Day 1 explainer.

Demonstrates that a generic LLM judge's scores change when:
  1. The agent output is moved BEFORE the input context (position swap)
  2. The agent output is padded with filler to double its length (length bias)

Uses 5 tasks from tenacious_bench_v0.1/dev.jsonl.
Compares DeepSeek Chat v3 (generic) vs Claude Sonnet 4.6 (production judge).

Usage:
    cd g:/projects/week11/sales-agent-evaluation-bench
    python ../conversion-engine/pair_DAY_1/position_bias_experiment.py

Requires: OPENROUTER_API_KEY in .env
Cost estimate: ~$0.02-0.05 (5 tasks × 4 conditions × 2 models × ~500 tokens)
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from the bench repo
projects_root = Path(__file__).resolve().parents[3]
load_dotenv(projects_root / "week11" / "sales-agent-evaluation-bench" / ".env")
# Fallback: also try the conversion-engine .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
    sys.exit(1)

# ── Models to compare ────────────────────────────────────────────────
MODELS = {
    "deepseek": "deepseek/deepseek-chat",   # generic judge (partner's model)
    "claude":   "anthropic/claude-sonnet-4-6",             # production judge (your baseline)
}

# ── Prompt templates ─────────────────────────────────────────────────

SYSTEM_PREAMBLE = """You are a Tenacious sales evaluation judge. Score the agent output on each rubric dimension 1–5.

SCORING ANCHORS (all dimensions):
1 = Fails entirely — violation immediately visible to a CTO/VP reader
2 = Partially fails — violation present but partially mitigated
3 = Borderline — satisfies minimum; a careful reader would flag weaknesses
4 = Passes clearly — only minor non-material imperfections
5 = Exemplary — matches a labeled GOOD example in Tenacious Style Guide v2

KEY RULES FROM TENACIOUS STYLE GUIDE v2:
- "bench" must NOT appear externally; use "engineering team" or "available capacity"
- signal_confidence < 0.6 → interrogative/conditional language only
- signal_confidence ≥ 0.6 → assertive language permitted
- Cold outreach body ≤ 120 words; warm reply ≤ 200 words
- One ask per message; no stacking
- Capacity commitments must not exceed bench_summary available_engineers per stack

Return ONLY a JSON object with integer scores 1–5:
{"tone_adherence": int, "signal_grounding": int, "bench_honesty": int, "icp_accuracy": int, "completeness": int}
No markdown. No explanation."""


def build_normal_prompt(task: dict, output: str) -> str:
    """Normal order: context → ground_truth → output → rubric (your production layout)."""
    rubric = task.get("evaluator_config", {}).get("rubric", [])
    return (
        f"INPUT CONTEXT:\n{json.dumps(task.get('input_context', {}), indent=2)}\n\n"
        f"GROUND TRUTH:\n{json.dumps(task.get('ground_truth', {}), indent=2)}\n\n"
        f"AGENT OUTPUT:\n{output}\n\n"
        f"RUBRIC (score each dimension 1–5):\n{json.dumps(rubric, indent=2)}"
    )


def build_swapped_prompt(task: dict, output: str) -> str:
    """Swapped order: output FIRST → rubric → context → ground_truth."""
    rubric = task.get("evaluator_config", {}).get("rubric", [])
    return (
        f"AGENT OUTPUT:\n{output}\n\n"
        f"RUBRIC (score each dimension 1–5):\n{json.dumps(rubric, indent=2)}\n\n"
        f"INPUT CONTEXT:\n{json.dumps(task.get('input_context', {}), indent=2)}\n\n"
        f"GROUND TRUTH:\n{json.dumps(task.get('ground_truth', {}), indent=2)}"
    )


def pad_output(output: str) -> str:
    """Double the output length with plausible but vacuous filler sentences."""
    filler = (
        " We pride ourselves on maintaining the highest standards of engineering excellence "
        "across all our engagements. Our team has consistently delivered results that speak "
        "for themselves, and we look forward to exploring how we can bring similar value to "
        "your organization. Each engagement is tailored to the specific needs and goals of "
        "our clients, ensuring maximum impact and alignment with their strategic objectives."
    )
    return output + filler


# ── LLM call ─────────────────────────────────────────────────────────

def call_judge(model_key: str, user_prompt: str, retries: int = 2) -> dict | None:
    """Call OpenRouter and return parsed dimension scores, or None on failure."""
    model = MODELS[model_key]
    for attempt in range(retries + 1):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PREAMBLE},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": 128,
                    "temperature": 0.0,
                },
                timeout=60,
            )
            data = resp.json()

            if "error" in data:
                print(f"    [retry {attempt}] API error: {data['error']}")
                time.sleep(2 ** attempt)
                continue

            raw = data["choices"][0]["message"]["content"].strip()
            raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("```").strip()
            scores = {k: int(v) for k, v in json.loads(raw).items()}
            return scores

        except Exception as exc:
            print(f"    [retry {attempt}] {exc}")
            time.sleep(2 ** attempt)

    return None


# ── Main experiment ──────────────────────────────────────────────────

def load_dev_tasks(n: int = 5) -> list[dict]:
    """Load first N tasks from dev.jsonl that have expected_pass=False (failing tasks)."""
    # Fix: Correctly find the sibling week11 directory from g:/projects
    # Current file: g:/projects/week10/conversion-engine/pair_DAY_1/position_bias_experiment.py
    # .parents[3] gets us to g:/projects
    projects_root = Path(__file__).resolve().parents[3]
    bench_dir = projects_root / "week11" / "sales-agent-evaluation-bench"
    dev_path = bench_dir / "tenacious_bench_v0.1" / "dev.jsonl"
    if not dev_path.exists():
        print(f"ERROR: {dev_path} not found", file=sys.stderr)
        sys.exit(1)

    tasks = []
    with open(dev_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            task = json.loads(line)
            # Use only failing tasks — these have clear violations to judge
            if task.get("expected_pass") is False:
                tasks.append(task)
            if len(tasks) >= n:
                break
    return tasks


def run_experiment():
    tasks = load_dev_tasks(5)
    print(f"Loaded {len(tasks)} failing dev tasks\n")

    results = []

    for i, task in enumerate(tasks):
        task_id = task["task_id"]
        category = task.get("metadata", {}).get("category", "")
        output = task.get("candidate_output", "")
        padded = pad_output(output)

        print(f"== Task {i+1}/{len(tasks)}: {task_id} ({category}) ==")
        print(f"   Output length: {len(output.split())} words")
        print(f"   Padded length: {len(padded.split())} words\n")

        # Build 3 prompt variants
        prompt_normal = build_normal_prompt(task, output)
        prompt_swapped = build_swapped_prompt(task, output)
        prompt_lengthened = build_normal_prompt(task, padded)

        task_result = {
            "task_id": task_id,
            "category": category,
            "expected_pass": task.get("expected_pass"),
            "output_word_count": len(output.split()),
            "padded_word_count": len(padded.split()),
            "scores": {},
        }

        for model_key in MODELS:
            print(f"   Model: {model_key}")

            # Condition A: Normal order
            print(f"     [A] Normal order...", end=" ", flush=True)
            scores_normal = call_judge(model_key, prompt_normal)
            print(f"{scores_normal}")
            time.sleep(1)  # rate limit courtesy

            # Condition B: Swapped order (output first)
            print(f"     [B] Swapped order...", end=" ", flush=True)
            scores_swapped = call_judge(model_key, prompt_swapped)
            print(f"{scores_swapped}")
            time.sleep(1)

            # Condition C: Padded output (length bias)
            print(f"     [C] Padded output...", end=" ", flush=True)
            scores_padded = call_judge(model_key, prompt_lengthened)
            print(f"{scores_padded}")
            time.sleep(1)

            task_result["scores"][model_key] = {
                "normal": scores_normal,
                "swapped": scores_swapped,
                "padded": scores_padded,
            }
            print()

        results.append(task_result)

    # ── Summary statistics ───────────────────────────────────────────
    print("\n" + "=" * 70)
    print("POSITION BIAS SUMMARY")
    print("=" * 70)

    for model_key in MODELS:
        position_diffs = []
        length_diffs = []

        for r in results:
            s = r["scores"].get(model_key, {})
            normal = s.get("normal")
            swapped = s.get("swapped")
            padded = s.get("padded")

            if normal and swapped:
                for dim in normal:
                    diff = swapped.get(dim, 0) - normal.get(dim, 0)
                    position_diffs.append((r["task_id"], dim, normal[dim], swapped[dim], diff))

            if normal and padded:
                for dim in normal:
                    diff = padded.get(dim, 0) - normal.get(dim, 0)
                    length_diffs.append((r["task_id"], dim, normal[dim], padded[dim], diff))

        print(f"\n-- {model_key.upper()} ({MODELS[model_key]}) --")

        # Position bias
        changed = [d for d in position_diffs if d[4] != 0]
        print(f"\n  Position bias (normal vs swapped):")
        print(f"    Total dimension scores compared: {len(position_diffs)}")
        print(f"    Scores that CHANGED on swap:     {len(changed)} ({100*len(changed)/max(len(position_diffs),1):.0f}%)")
        if changed:
            avg_shift = sum(d[4] for d in changed) / len(changed)
            print(f"    Average shift when changed:      {avg_shift:+.1f}")
            print(f"    Direction: {'output-first scores HIGHER' if avg_shift > 0 else 'output-first scores LOWER'}")
            print(f"\n    Changed scores:")
            for task_id, dim, norm, swap, diff in changed:
                print(f"      {task_id} / {dim}: {norm} -> {swap} ({diff:+d})")

        # Length bias
        changed_len = [d for d in length_diffs if d[4] != 0]
        print(f"\n  Length bias (normal vs padded):")
        print(f"    Total dimension scores compared: {len(length_diffs)}")
        print(f"    Scores that CHANGED on padding:  {len(changed_len)} ({100*len(changed_len)/max(len(length_diffs),1):.0f}%)")
        if changed_len:
            avg_shift = sum(d[4] for d in changed_len) / len(changed_len)
            print(f"    Average shift when changed:      {avg_shift:+.1f}")
            print(f"    Direction: {'longer output scores HIGHER' if avg_shift > 0 else 'longer output scores LOWER'}")
            print(f"\n    Changed scores:")
            for task_id, dim, norm, pad, diff in changed_len:
                print(f"      {task_id} / {dim}: {norm} -> {pad} ({diff:+d})")

    # ── Save results ─────────────────────────────────────────────────
    output_path = Path(__file__).parent / "position_bias_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    run_experiment()
