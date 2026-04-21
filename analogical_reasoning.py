#!/usr/bin/env python
# coding: utf-8

# Analogical Reasoning inference technique

from api import llm_caller


def run_analogical(question: str) -> str:

    # Step 1: Ask the model to recall or construct analogous examples
    analogy_sys = (
        "You are an expert at finding analogies. "
        "Given a problem, generate 2-3 similar but simpler worked examples "
        "that illustrate the same reasoning pattern. "
        "Show the full solution for each example."
    )
    analogy_prompt = (
        f"I need to solve this problem:\n\n{question}\n\n"
        "Before solving it, generate 2-3 analogous worked examples that use "
        "the same type of reasoning. Label them Example 1, Example 2, etc., "
        "and fully solve each one."
    )
    analogies = llm_caller(analogy_prompt, analogy_sys, temp=0.3)

    # Step 2: Use the analogies to solve the actual question
    solve_sys = (
        "You are a careful reasoning assistant. "
        "Use the provided examples as a guide to solve the new problem. "
        "Follow the same reasoning pattern shown in the examples. "
        "End with: ANSWER: <final answer>"
    )
    solve_prompt = (
        f"Here are some worked examples that use the same reasoning pattern:\n\n"
        f"{analogies}\n\n"
        f"Now solve this problem using the same approach:\n\n{question}\n\n"
        "End with: ANSWER: <final answer>"
    )
    result = llm_caller(solve_prompt, solve_sys, temp=0.0)

    if "ANSWER:" in result:
        return result.split("ANSWER:")[-1].strip()
    return result
