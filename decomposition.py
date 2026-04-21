from api import llm_caller

# 2 calls
def run_decomp(question: str) -> str:
    system_prompt=(
        "You are a reasoning agent that decomposes problems into smaller, more manageable steps before solving. "
        "Do NOT solve the problem yet."
    )

    get_steps = (
        "Break the following question down into a few numbered steps. "
        "For example: 1. step description, 2. step description\n\n"
        f"{question}\n\n"
    )
    steps = llm_caller(get_steps, system_prompt)

    solve_prob = (
        f"{question}\n\n"
        f"{steps}\n\n"
        "Return the final answer in format: ANSWER: <answer>"
    )
    answer = llm_caller(solve_prob, "Solve the question with the given steps.")

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()
    return answer.strip()