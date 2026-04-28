from api import llm_caller
import ast
import operator as op
import re

# added safer calc option from mini lab 5
ALLOWED_BINOPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod}
ALLOWED_UNOPS  = {ast.UAdd: op.pos, ast.USub: op.neg}

def calculator(expr: str):
    expr = expr.strip()
    expr = (
    expr.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("^", "**")
    )
    expr = re.sub(r"[^0-9+\-*/(). ]", "", expr)
    expr = re.sub(r"(\d)\s+(\d)", r"\1*\2", expr)  # if input is something like 10 10, change to 10*10
    
    if " " in expr and any(op in expr for op in ["+", "-", "*", "/"]) is False:
        raise ValueError(f"Not a valid expression")

    if len(expr) > 200:
        raise ValueError("Expression too long")

    node = ast.parse(expr, mode="eval")

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.UnaryOp) and type(n.op) in ALLOWED_UNOPS:
            return ALLOWED_UNOPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in ALLOWED_BINOPS:
            return ALLOWED_BINOPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "round":
            args = [_eval(a) for a in n.args]
            return round(*args)
        raise ValueError("Unable to evaluate expression.")

    return _eval(node)


def run_tool_augmented(question: str) -> str:
    system = (
        "You are a reasoning agent with access to tools. "
        "You decide whether a calculator is required to answer a question."
    )

    decision_prompt = (
        "Does the following question require a calculation? "
        "Retun ONLY 'yes' or 'no'.\n\n"
        f"{question}"
    )
    decision = llm_caller(decision_prompt, system, temp=0.0).strip().lower()

    if "yes" in decision.lower():
        expr_prompt = (
            f"Question: {question}\n\n"
            "Create a valid math expression by following what the question asks carefully.\n\n"
            "Avoid expressions where the denominator becomes 0 or undefined. "
            "Do NOT include words. Convert percentages to decimal if necessary.\n\n"
            "Return ONLY a clean arithmetic expression. NO unecessary fluff"
        )
        expr = llm_caller(expr_prompt, "You carefully extract math expressions", 0.0).strip()

        try:
            result = calculator(expr)
        except:
            result = llm_caller(f"Solve and return ONLY the final number, no reasoning.\nExpression: {expr}", "You are a professional mathematician that solves math equations",0.0).strip()

        return str(result).strip()

    answer_prompt = (
        f"Question: {question}\n\n"
        "Solve and return ONLY the correct answer in format: ANSWER: <final answer>, unless the question specifies how to return. DO NOT return how you got the answer."
    )

    answer = llm_caller(answer_prompt, "You carefully read then answer the question, answer by using what is provided", 0.0)

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()

    return answer.strip()