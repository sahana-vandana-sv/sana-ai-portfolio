"""Evaluation suite — run with: python -m eval.eval_suite"""

import asyncio
import json
import os
from pathlib import Path

from agents.supervisor import supervisor_node
from agents.state import AgentState


DATASET_PATH = Path(__file__).parent / "dataset.json"


def _overlap_score(predicted: dict, expected: dict) -> float:
    keys = list(expected.keys())
    if not keys:
        return 1.0
    correct = sum(1 for k in keys if predicted.get(k) == expected.get(k))
    return correct / len(keys)


async def evaluate_case(case: dict) -> dict:
    state: AgentState = {
        "user_id": "eval_user",
        "chat_id": "eval_chat",
        "message": case["input"],
        "routing": None,
        "short_term_context": [],
        "results": [],
        "reply": "",
        "error": None,
    }
    result = await supervisor_node(state)
    routing = result["routing"]
    predicted = routing.model_dump() if routing else {}
    expected = case["expected_routing"]
    score = _overlap_score(predicted, expected)
    return {
        "input": case["input"],
        "expected": expected,
        "predicted": {k: predicted.get(k) for k in expected},
        "score": score,
        "pass": score == 1.0,
    }


async def run_eval():
    dataset = json.loads(DATASET_PATH.read_text())
    results = await asyncio.gather(*[evaluate_case(c) for c in dataset])

    passed = sum(1 for r in results if r["pass"])
    accuracy = passed / len(results)

    print(f"\n{'='*60}")
    print(f"LifeAgent Evaluation — {len(results)} cases")
    print(f"Accuracy: {accuracy:.1%}  ({passed}/{len(results)} passed)")
    print(f"{'='*60}")

    failures = [r for r in results if not r["pass"]]
    if failures:
        print("\nFailed cases:")
        for f in failures:
            print(f"  Input:     {f['input']}")
            print(f"  Expected:  {f['expected']}")
            print(f"  Predicted: {f['predicted']}")
            print()

    return accuracy


if __name__ == "__main__":
    asyncio.run(run_eval())
