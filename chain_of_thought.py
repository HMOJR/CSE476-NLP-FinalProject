#!/usr/bin/env python
# coding: utf-8

# In[19]:


# Created by Hector Orozco (1 of 3 chosen inference techniques)
from api import llm_caller


# In[21]:


def run_cot(question: str) -> str:
    # This chain of thought inferencial technique is simple producing step-by-step reasoning to answer
    system_prompt=(
        "You are a very smart reasoning assistant."
        "Think step by step carefully."
        "After reasoning, return final answer in format: ANSWER: <answer>."
    )
    user_prompt=(
        f"Solve this problem step by step:\n\n"
        f"{question}\n\n"
        "Do NOT return steps used. Return only final answer in format: ANSWER: <final answer>"
    )
    # Final answer
    txt=llm_caller(user_prompt,system_prompt)
    if "ANSWER:"in txt:
        return txt.split("ANSWER:")[-1].strip()
    return txt


# In[ ]:




