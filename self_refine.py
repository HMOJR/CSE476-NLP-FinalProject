#!/usr/bin/env python
# coding: utf-8

# Self-Refine inference technique

from api import llm_caller

MAX_ROUNDS = 3


def run_self_refine(question: str) -> str:

    # Step 1: Generate initial answer
    init_sys = (
        "You are a careful reasoning assistant. "
        "Answer the question as best you can. "
        "End your response with the final answer in the format: ANSWER: <final answer>"
    )
    init_prompt = f"Question: {question}\n\nAnswer step by step, then end with the answer formatted: ANSWER: <final answer>"
    answer = llm_caller(init_prompt, init_sys, temp=0.0)

    for _ in range(MAX_ROUNDS):

        # Step 2: Critique the current answer
        critique_sys = (
            "You are a critical evaluator. "
            "Review the answer below for logical errors, missing steps, or inaccuracies. "
            "If the answer is correct and complete, reply only with: LGTM\n"
            "Otherwise, provide a short list of specific issues to fix."
        )
        critique_prompt = (
            f"Question: {question}\n\n"
            f"Current Answer:\n{answer}\n\n"
            "Is this answer correct and complete? If not, what needs to be fixed?"
        )
        critique = llm_caller(critique_prompt, critique_sys, temp=0.0)

        # Stop early if the model is satisfied
        if "LGTM" in critique.upper():
            break

        # Step 3: Refine based on critique
        refine_sys = (
            "You are a careful reasoning assistant. "
            "You will be given a question, a previous answer, and feedback on that answer. "
            "Find an improved answer using the feedback. "
            "Do NOT include reasoning in final answer. Return ONLY your final answer in the format: ANSWER: <final answer>"
        )
        refine_prompt = (
            f"Question: {question}\n\n"
            f"Previous Answer:\n{answer}\n\n"
            f"Feedback:\n{critique}\n\n"
            "Return ONLY the correct final answer, NO reasoning, in the format: ANSWER: <final answer>"
        )
        answer = llm_caller(refine_prompt, refine_sys, temp=0.0)

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()
    return answer
