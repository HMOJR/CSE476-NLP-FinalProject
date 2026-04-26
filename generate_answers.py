#!/usr/bin/env python3
"""
Generate a placeholder answer file that matches the expected auto-grader format.

Replace the placeholder logic inside `build_answers()` with your own agent loop
before submitting so the ``output`` fields contain your real predictions.

Reads the input questions from cse_476_final_project_test_data.json and writes
an answers JSON file where each entry contains a string under the "output" key.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from api import llm_caller

from chain_of_thought import run_cot
from self_consistency import run_scy
from tree_of_thought import run_tot
from self_refine import run_self_refine
from analogical_reasoning import run_analogical
from self_debug import run_self_debug
from react import run_react
from decomposition import run_decomp
from tool_augmented import run_tool_augmented

INPUT_PATH = Path("cse_476_final_project_test_data.json")
OUTPUT_PATH = Path("cse_476_final_project_answers.json")


def load_questions(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, list):
        raise ValueError("Input file must contain a list of question objects.")
    return data

# 1 initial call to the llm
def agent_loop(question:str) -> str:
    system = (
        "You are a router deciding what the best approach to solving a question is.\n\n"
        "Select the BEST strategy (1-9) for solving the question from the list below:\n\n"
        "1. Chain-of-Thought\n\n"
        "2. Self-Consistency\n\n"
        "3. Tree-of-Thought\n\n"
        "4. Self-Refine\n\n"
        "5. Analogical Reasoning\n\n"
        "6. Self-Debug: for debugging and python rather than creating new code\n\n"
        "7. ReAct\n\n"
        "8. Decomposition\n\n"
        "9. Tool-Augmented\n\n"

        "If unsure or if more convenient to save calls, return 7\n\n"
        "Return ONLY the number, NO trailing period.\n\n"
        f"{question}"
    )

    try:
        result = llm_caller("Return ONLY the number", system, 0.0).strip()

        result = result.replace(".", "")
        result = result.split()[0]
    except:
        result = "7"  # default react

    if result == "1":
        return run_cot(question)
    elif result == "2":
        return run_scy(question)
    elif result == "3":
        return run_tot(question)
    elif result == "4":
        return run_self_refine(question)
    elif result == "5":
        return run_analogical(question)
    elif result == "6":
        return run_self_debug(question)
    elif result == "7":
        return run_react(question)
    elif result == "8":
        return run_decomp(question)
    elif result == "9":
        return run_tool_augmented(question)

    return run_react(question)


def build_answers(questions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    if OUTPUT_PATH.exists():
        with OUTPUT_PATH.open("r", encoding="utf-8") as fp:
            answers = json.load(fp)
    else:
        answers = []

    answers = answers[:5719] 
    start_idx = len(answers)

    for idx, question in enumerate(questions):
        if idx < start_idx:
            continue

        try:
            real_answer = agent_loop(question["input"])
        except Exception as e:
            real_answer = f"ERROR: {e}"

        answers.append({"output": real_answer})

        # save frequently
        if (idx - start_idx) % 20 == 0:
            with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
                json.dump(answers, fp, ensure_ascii=False, indent=2)

        print(f"{idx+1}/{len(questions)} done")

    return answers


def validate_results(
    questions: List[Dict[str, Any]], answers: List[Dict[str, Any]]
) -> None:
    if len(questions) != len(answers):
        raise ValueError(
            f"Mismatched lengths: {len(questions)} questions vs {len(answers)} answers."
        )
    for idx, answer in enumerate(answers):
        if "output" not in answer:
            raise ValueError(f"Missing 'output' field for answer index {idx}.")
        if not isinstance(answer["output"], str):
            raise TypeError(
                f"Answer at index {idx} has non-string output: {type(answer['output'])}"
            )
        if len(answer["output"]) >= 5000:
            raise ValueError(
                f"Answer at index {idx} exceeds 5000 characters "
                f"({len(answer['output'])} chars). Please make sure your answer does not include any intermediate results."
            )


def main() -> None:
    questions = load_questions(INPUT_PATH)
    answers = build_answers(questions)

    with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        json.dump(answers, fp, ensure_ascii=False, indent=2)

    with OUTPUT_PATH.open("r", encoding="utf-8") as fp:
        saved_answers = json.load(fp)
    validate_results(questions, saved_answers)
    print(
        f"Wrote {len(answers)} answers to {OUTPUT_PATH} "
        "and validated format successfully."
    )


if __name__ == "__main__":
    main()

