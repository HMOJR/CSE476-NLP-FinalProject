from api import llm_caller
import ast
import operator as op
import re

# added safer calc option from mini lab 5
ALLOWED_BINOPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod}
ALLOWED_UNOPS  = {ast.UAdd: op.pos, ast.USub: op.neg}

def calculator(expr: str):
    expr = expr.strip()
    expr = expr.replace("^", "**")
    expr = re.sub(r"[^0-9+\-*/().^ ]", "", expr)
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
        "Does the following question require a calculator? "
        "Answer ONLY with 'yes' or 'no'.\n\n"
        f"{question}"
    )
    decision = llm_caller(decision_prompt, system, temp=0.0).strip().lower()

    if "yes" in decision.lower():
        expr_prompt = (
            "Extract a math expression from the question like: 4 + 5 * (5 - 4) "
            "Return ONLY the math expression.\n\n"
            f"{question}"
        )
        expr = llm_caller(expr_prompt, system, temp=0.0).strip()

        try:
            result = calculator(expr)
            return str(result)
        except:
            compute = llm_caller(f"Do not include reasoning. Compute this problem and return numeric answer ONLY: {question}", system,temp=0.0)
            return compute.strip()

    # if tool is not needed
    answer_prompt = (
        f"{question}\n\n"
        "DO NOT include the expression.\n\n" 
        "Return the shortest possible answer in the format: ANSWER: <final answer>"
    )
    answer = llm_caller(answer_prompt, system, temp=0.0)

    if "ANSWER:" in answer:
        return answer.split("ANSWER:")[-1].strip()
    
    return answer.split("\n")[-1].strip()