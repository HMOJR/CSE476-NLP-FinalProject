#!/usr/bin/env python
# coding: utf-8

# Self-Debug inference technique

import subprocess
import sys
import re
from api import llm_caller
from react import run_react
 
MAX_DEBUG_ROUNDS = 3
 
 
def _try_execute_python(code: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)
 
 
def _extract_code(text: str) -> str | None:
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
 
 
def run_self_debug(question: str) -> str:
 
    # Step 1: Generate initial solution
    gen_sys = (
        "You are a skilled problem solver. "
        "If the problem requires a function to be written in Python, write a Python script without extra explanations or markdown "
        "inside a ```python ... ``` code block. "
        "If it cannot be solved right away, reason step by step to correct and return either the code block, function, or the final answer in the format: ANSWER: final answer"
    )
    gen_prompt = f"Solve the following problem:\n\n{question}"
    solution = llm_caller(gen_prompt, gen_sys, temp=0.0)
 
    # Check if there's executable code to try
    code = _extract_code(solution)
 
    if code:
        # Code path: execute and debug
        for _ in range(MAX_DEBUG_ROUNDS):
            success, output = _try_execute_python(code)
            if success and output:
                return output
 
            # Ask model to explain the bug and fix it
            debug_sys = (
                "You are an expert Python debugger. "
                "You will be shown code and an error. "
                "Explain what is wrong, then provide a corrected version "
                "inside a ```python ... ``` block."
            )
            debug_prompt = (
                f"Problem: {question}\n\n"
                f"Code:\n```python\n{code}\n```\n\n"
                f"Error:\n{output}\n\n"
                "Explain the bug and provide a fixed version."
            )
            debug_response = llm_caller(debug_prompt, debug_sys, temp=0.0)
            new_code = _extract_code(debug_response)
            if new_code:
                code = new_code
            else:
                break
 
        # If code still fails, fall through to text reasoning
        success, output = _try_execute_python(code)
        if success and output:
            return output.strip()
 
    # Text/reasoning path: use execution trace simulation
    solution_text = solution
    for _ in range(MAX_DEBUG_ROUNDS):
        trace_sys = (
            "You are a meticulous reasoning checker. "
            "Walk through the solution step by step, stating what each step produces. "
            "If you find an error, state: BUG FOUND: <description>. "
            "If the solution is correct, state: NO BUGS FOUND."
        )
        trace_prompt = (
            f"Problem: {question}\n\n"
            f"Solution to check:\n{solution_text}\n\n"
            "Trace through each step. If you find a bug, describe it."
        )
        trace = llm_caller(trace_prompt, trace_sys, temp=0.0)
 
        if "NO BUGS FOUND" in trace.upper():
            break
 
        # Fix the identified bug
        fix_sys = (
            "You are a careful problem solver. "
            "You will be given a problem, a flawed solution, and a bug report. "
            "Produce a corrected solution. Return the answer in the format asked for, or if not mentioned, return in the format: ANSWER: final answer"
        )
        fix_prompt = (
            f"Problem: {question}\n\n"
            f"Flawed solution:\n{solution_text}\n\n"
            f"Bug report:\n{trace}\n\n"
            "Return the final corrected solution in the format asked for, or if not mentioned, return in the format: ANSWER: final answer"
        )
        solution_text = llm_caller(fix_prompt, fix_sys, temp=0.0)
 
    if "ANSWER:" in solution_text:
        return solution_text.split("ANSWER:")[-1].strip()
    # Fallback: return the last non-empty line
    return run_react(question)
 