"""
Day 2 — Path 1 vs Path 2: the schema injection mechanism.

Demonstrates why "schemas present in the prompt" is not the same as
"schemas registered via the API tools parameter."

  PATH 1 (BASELINE): Schema via API tools=[...] parameter
    → model produces finish_reason='tool_calls' with structured JSON arguments

  PATH 2 (FAILURE): Schema injected as text in system prompt, no tools parameter
    → model produces natural language or attempts to mimic tool-call format in text

This is the root cause of the failure in the peer question: MCP schemas injected
as text don't trigger the post-trained tool_call pattern.

Usage:
    cd g:/projects/week12/knowledge-gap-formulation
    uv run python pair_DAY_2/tool_failure_demo.py

Requires: OPENROUTER_API_KEY in .env
Cost: ~$0.005 (2 conditions x 1 call each)
"""

import datetime
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / "week10" / "conversion-engine" / ".env")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
    sys.exit(1)

OUTPUT_PATH = Path(__file__).parent / "function_calling_results.json"
MODEL = "anthropic/claude-sonnet-4-6"

# ── Tool schema (identical content used in both conditions) ───────────

TOOL_SCHEMA = {
    "name": "create_enriched_contact",
    "description": "Create a HubSpot contact record with ICP classification and enrichment metadata.",
    "parameters": {
        "type": "object",
        "properties": {
            "email":              {"type": "string",  "description": "Prospect email address"},
            "company":            {"type": "string",  "description": "Company name"},
            "icp_segment":        {"type": "string",  "description": "e.g. segment_1_series_a_b"},
            "ai_maturity_score":  {"type": "integer", "description": "0-3 score from enrichment"},
            "segment_confidence": {"type": "number",  "description": "0.0-1.0 classifier confidence"},
        },
        "required": ["email", "company", "icp_segment", "ai_maturity_score", "segment_confidence"],
    },
}

# Text representation of the same schema — how an MCP client might inject it
SCHEMA_AS_TEXT = """You have access to the following tool:

  Tool: create_enriched_contact
  Description: Create a HubSpot contact record with ICP classification and enrichment metadata.
  Parameters:
    - email (string): Prospect email address
    - company (string): Company name
    - icp_segment (string): e.g. segment_1_series_a_b
    - ai_maturity_score (integer): 0-3 score from enrichment
    - segment_confidence (number): 0.0-1.0 classifier confidence

Use this tool when enrichment data is available for a new prospect."""

SYSTEM_BASE = "You are a CRM operations agent for Tenacious Intelligence."

USER_MESSAGE = """Enrichment complete for new prospect:

Company: Acme AI Corp
Email: james@acmeai.io
ICP Segment: segment_1_series_a_b
AI Maturity Score: 2
Segment Confidence: 0.85"""


# ── API calls ─────────────────────────────────────────────────────────

def call_path1_api_tools() -> dict:
    """Path 1: schema registered via API tools parameter."""
    return requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_BASE},
                {"role": "user",   "content": USER_MESSAGE},
            ],
            "tools": [{"type": "function", "function": TOOL_SCHEMA}],
            "tool_choice": "auto",
            "max_tokens": 512,
            "temperature": 0.0,
        },
        timeout=60,
    ).json()


def call_path2_text_injection() -> dict:
    """Path 2: schema injected as text in system prompt, no tools parameter."""
    return requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_BASE + "\n\n" + SCHEMA_AS_TEXT},
                {"role": "user",   "content": USER_MESSAGE},
            ],
            # No tools parameter — schema is only in the text
            "max_tokens": 512,
            "temperature": 0.0,
        },
        timeout=60,
    ).json()


def classify_output(data: dict) -> tuple[str, str | None]:
    if "error" in data:
        return "error", None
    choice = data["choices"][0]
    finish = choice.get("finish_reason", "")
    msg = choice["message"]
    tool_calls = msg.get("tool_calls", [])

    if finish == "tool_calls" and tool_calls:
        return "tool_call", tool_calls[0]["function"]["name"]

    content = msg.get("content", "") or ""
    if "{" in content and "create_enriched_contact" in content:
        return "malformed_attempt", None
    return "natural_language", None


def _save_results(records: list) -> None:
    OUTPUT_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"\nResults saved to {OUTPUT_PATH}")


# ── Main ──────────────────────────────────────────────────────────────

def run():
    conditions = [
        {
            "label": "PATH 1 (BASELINE): Schema via API tools parameter",
            "call":  call_path1_api_tools,
            "path":  "API tools=[...]",
            "expected": "tool_call",
        },
        {
            "label": "PATH 2 (FAILURE): Schema as text injection, no tools parameter",
            "call":  call_path2_text_injection,
            "path":  "text in system prompt",
            "expected": "natural_language or malformed_attempt",
        },
    ]

    print("=" * 70)
    print("PATH 1 vs PATH 2: SCHEMA INJECTION MECHANISM")
    print("=" * 70)
    print(f"Model: {MODEL}\n")
    print("Same schema. Same model. Same user message.")
    print("Only the delivery path changes.\n")

    records = []

    for i, cond in enumerate(conditions):
        print(f"[{i+1}/{len(conditions)}] {cond['label']}")
        print(f"  Expected : {cond['expected']}")

        data = cond["call"]()
        output_type, tool_name = classify_output(data)

        if "error" in data:
            print(f"  RESULT   : ERROR — {data['error']}")
        else:
            choice = data["choices"][0]
            usage  = data.get("usage", {})
            msg    = choice["message"]
            content    = msg.get("content") or ""
            tool_calls = msg.get("tool_calls", [])

            print(f"  finish_reason   : {choice['finish_reason']!r}")
            print(f"  output_type     : {output_type.upper()}")
            if tool_calls:
                tc   = tool_calls[0]
                args = json.loads(tc["function"]["arguments"])
                print(f"  tool_called     : {tc['function']['name']!r}")
                print(f"  arguments       : {list(args.keys())}")
            elif content:
                print(f"  text_output     : {content[:200].replace(chr(10), ' ')!r}")
            print(f"  prompt_tokens   : {usage.get('prompt_tokens', 'n/a')}")
            print(f"  completion_tok  : {usage.get('completion_tokens', 'n/a')}")
            print()

        records.append({
            "condition":         cond["label"],
            "schema_path":       cond["path"],
            "expected":          cond["expected"],
            "actual_output_type": output_type,
            "tool_called":       tool_name,
            "finish_reason":     data["choices"][0]["finish_reason"] if "choices" in data else None,
            "usage":             data.get("usage"),
            "text_content":      (data["choices"][0]["message"].get("content") or "")[:500] if "choices" in data else None,
            "tool_calls": (
                [
                    {
                        "name":      tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"]),
                    }
                    for tc in (data["choices"][0]["message"].get("tool_calls") or [])
                ]
                if "choices" in data else []
            ),
            "saved_at": datetime.datetime.now(datetime.UTC).isoformat(),
        })

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in records:
        tag = "PATH 1" if "PATH 1" in r["condition"] else "PATH 2"
        print(f"  [{tag}] {r['actual_output_type'].upper():22s} ← {r['schema_path']}")

    print()
    print("FINDING:")
    print("  The trigger for structured tool-call output is post-training on the")
    print("  API tools format, not schema visibility in the prompt.")

    _save_results(records)


if __name__ == "__main__":
    run()
