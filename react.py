#!/usr/bin/env python3
import re
from api import llm_caller
from tool_augmented import calculator

def run_react(question: str) -> str:

    system = "You are a reasoning agent that follows thought + action + reflection and reads questions carefully."

    action_prompt = (
        "Think logically about what the question is asking, then decide an action based on if computation is needed or not."     
        f"Question: {question}\n\n"
        "Follow this format:\n\n"
        "Thought: <reasoning>\n\n"
        "Action: <calc | none>\n\n"
        "Expression: <arithmetic expression>"
    )

    action_choice = llm_caller(action_prompt, "carefully select an action as expressions get calculated if calc is selected",temp=0.2)
    action = "none"
    expr = ""

    for line in action_choice.splitlines():
        if line.lower().startswith("action"):
            if "calc" in line.lower():
                action = "calc"
            else:
                action = "none"

        if line.lower().startswith("expression"):
            expr = line.split(":", 1)[-1].strip()

    if action == "calc" and expr and expr.lower() != "none":
        try:
            observation = calculator(expr)
        except: 
            observation= llm_caller(f"Compute this problem: {expr}", "You are a mathematician carefully calculating a problem by hand", temp=0.0)


        reflection_prompt = (
            f"Question: {question}\n\n"
            f"Observation: {observation}\n\n"
            "Reflect on the observation and if it is logically sound. If it is invalid or does not correctly answer the question, "
            "return the corrected final answer, without including actions, thoughts, or observations, in the format: ANSWER: final answer\n\n"
        )
        answer = llm_caller(reflection_prompt, system, temp=0.0)

    else:
        answer_prompt = (
            "Answer the following question, do not overcomplicate"
            f"Question: {question}\n\n"
            "DO NOT include explanations or reasonings in the returned final answer\n\n"
            "ONLY return the correct final answer in format: "
            "ANSWER: <final answer, function, or a simple expression if explicitly asked for>."
        )
        answer = llm_caller(answer_prompt, system, temp=0.0)

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()

    return answer.strip()