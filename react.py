#!/usr/bin/env python3
import re
from api import llm_caller
from tool_augmented import calculator

def run_react(question: str) -> str:

    system = "You are a reasoning agent that follows thought + action + reflection."

    action_prompt = (
        f"Question: {question}\n\n"
        "Think about the question, then decide an action. Follow this format:\n\n"
        "Thought: <reasoning>\n"
        "Action: calc | none\n"
        "Expression: <arithmetic expression if calc, otherwise none>"
    )

    action_choice = llm_caller(action_prompt, system,temp=0.0)
    action, expr = "", ""
    
    for line in action_choice.splitlines():
        if line.lower().startswith("action:"):
            action = line.split(":", 1)[1].strip().lower()
        elif line.lower().startswith("expression:"):
            expr = line.split(":", 1)[1].strip() # should only contain expression

    if action == "calc" and expr and expr.lower() != "none":
        try:
            observation = calculator(expr)
        except: 
            observation= llm_caller(f"Compute this problem: {question}", system,temp=0.0)


        reflection_prompt = (
            f"Question: {question}\n\n"
            f"Thought + Action:\n{action_choice}\n\n"
            f"Observation: {observation}\n\n"
            "Reflect on the observation and return the shortest possible final answer in the format: "
            "ANSWER: <final answer or expression>"
        )
        answer = llm_caller(reflection_prompt, system, temp=0.0)

    else:
        answer_prompt = (
            f"{question}\n\n"
            "DO NOT include explanations\n\n"
            "ONLY return the shortest possible final answer in format: "
            "ANSWER: <final answer, function, or expression>."
        )
        answer = llm_caller(answer_prompt, system, temp=0.0)

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()

    return answer.split("\n")[-1].strip()