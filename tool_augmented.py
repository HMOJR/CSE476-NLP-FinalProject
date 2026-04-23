from api import llm_caller

def calculator(expr):
    try:
        result = eval(expr, {"__builtins__": {}})
        return str(result)
    except:
        return "Unable to evaluate expression."


def run_tool_augmented(question: str) -> str:
    system = (
        "You are a reasoning agent with access to tools. "
        "You decide whether a calculator is required to answer a question."
    )

    decision_prompt = (
        "Does the following question require a calculator? "
        "Answer ONLY with 'yes' or 'no'.\n\n"
        f"{question}"
    )
    decision = llm_caller(decision_prompt, system, temp=0.0).strip().lower()

    if "yes" in decision:
        expr_prompt = (
            "Extract a math expression from the question like: 4 + 5 * (5 - 4) "
            "Return ONLY the math expression.\n\n"
            f"{question}"
        )
        expr = llm_caller(expr_prompt, system, temp=0.0).strip()
        return calculator(expr)

    # if tool is not needed
    answer_prompt = (
        f"{question}\n\n"
        "Return the answer in the format: ANSWER: <answer>"
    )
    answer = llm_caller(answer_prompt, system, temp=0.0)

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()
    return answer.strip()