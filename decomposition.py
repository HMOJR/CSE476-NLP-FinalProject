from api import llm_caller
import re
# 2 calls, fixed formatting issues
def run_decomp(question: str) -> str:
    system=(
        "You are a reasoning agent that decomposes problems into smaller, more manageable steps before solving. "
        "Do NOT solve the problem yet."
    )

    get_steps = (
        f"""
        Break the following question down into a few (3-5) numbered steps.
        Format:
        1. <step description>
        2. <step description>
        3. ...

        Question:
        {question}
        """
    )
    steps = llm_caller(get_steps, system)

    solve_prob = (
        f"""
        Solve the problem using the steps below.
        Question:
        {question}

        Steps:
        {steps}
        """
    )
    answer = llm_caller(solve_prob, "DO NOT include steps in answer. Return ONLY the shortest possible final answer in format: ANSWER: <final answer>")

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()
    
    return answer.split("\n")[-1].strip()