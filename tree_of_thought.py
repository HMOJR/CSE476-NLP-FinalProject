#!/usr/bin/env python
# coding: utf-8

# In[13]:


# Created by Hector Orozco (3 of 3 chosen inference techniques)
from api import llm_caller


# In[15]:


def run_tot(question: str) -> str:
    # To ensure stays within project scopes of <20 calls, efficiency
    BRANCHES=3
    EXPANSIONS=1
    EVALUATIONS=1
    # Initial thoughts
    init_t=[]
    for _ in range(BRANCHES):
        prompt=(
            f"Consider the problem:\n{question}\n\n"
            "Generate one possible reasoning path. "
            "Do NOT give the final answer yet. "
            "Label your output as: THOUGHT: <your reasoning>")
        txt=llm_caller(prompt, "You generate reasoning paths.",temp=0.2)
        #print("\n--> INITIAL THOUGHT <--\n",txt)
        init_t.append(txt)
    # Expand thoughts
    expand_t=[]
    for thought in init_t:
        prompt=(
            f"This is just a part of a reasoning path:\n{thought}\n\n"
            "Expand on this reasoning and move ever closer to a solution. "
            "Do NOT give the final answer yet. "
            "Label your output as: EXPANSION: <your reasoning>")
        txt=llm_caller(prompt, "You expand reasoning paths.",temp=0.2)
        #print("\n--> EXPANSION <--\n",txt)
        expand_t.append(txt)
    # EValuate thoughts
    score_t=[]
    for thought in expand_t:
        prompt=(
            f"Evaluate the quality of this here reasoning:\n{thought}\n\n"
            "Rate it appropriately 1-10 based on how correct and coherent it is. "
            "Respond now ONLY with a number. ")
        score=llm_caller(prompt, "You evaluated reasoning quality.",temp=0.0)
        #print("\n--> SCORE <--\n",txt)
        score_t.append(score)
    # Best thought picker
    bindex=0
    bscore=-1
    for i,s in enumerate(score_t):
        try:
            num=float(s.strip())
            if num>bscore:
                bscore=num
                bindex=i
        except:
            pass
    # Picked best thought 
    bthought=expand_t[bindex]
    # Final answer
    final_t=(
        f"Based on the following reasoning, give ONLY the final answer now:\n\n"
        f"{bthought}\n\n"
        "Respond as: ANSWER: <final answer>")
    # Final answer to tree of thought
    finale=llm_caller(final_t, "You extract the final answers.",temp=0.0)
    if "ANSWER:" in finale:
        return finale.split("ANSWER:")[-1].strip()
    return finale.strip()


# In[ ]:




