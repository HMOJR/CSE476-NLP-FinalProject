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
        Break the following question down into a few (3-5) numbered SHORT steps.
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
        
        DO NOT return anything else but the solution. NO intermediate steps in the final answer unless explicitly asked for.
        """
    )
    answer = llm_caller(solve_prob, "Return ONLY the correct, shortest version of the final answer in format: ANSWER: <final answer>")

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()
    
    return answer.strip()