#!/usr/bin/env python
# coding: utf-8

# In[13]:


# Created by Hector Orozco (2 of 3 chosen inference techniques)
from api import llm_caller
from chain_of_thought import run_cot
from collections import Counter


# In[15]:


def run_scy(question: str,samples:int=5) -> str:
    # Sample multiple (5) CoTs and votes on final true answer
    ans=[]
    for _ in range(samples):
        answs=run_cot(question)
        #print(f"[Sample {i+1}] {answs}")
        ans.append(answs)
    # Final answer
    counts=Counter(ans)
    finale,_=counts.most_common(1)[0]
    #print("All answers:", ans)
    return finale


# In[ ]:




