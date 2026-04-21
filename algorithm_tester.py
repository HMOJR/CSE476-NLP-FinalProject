#!/usr/bin/env python
# coding: utf-8

# In[1]:


from openai import OpenAI # type: ignore
# 3 Inference Algorithms Developed by Hector Orozco
from chain_of_thought import run_cot
from self_consistency import run_scy
from tree_of_thought import run_tot
# 3 Inference Algorithms Developed by Bharath Gowda
from self_refine import run_self_refine
from analogical_reasoning import run_analogical
from self_debug import run_self_debug
# 3 Inference Algorithms Developed by Melissa Diaz
from react import run_react
from decomposition import run_decomp
from tool_augmented import run_tool_augmented


# In[17]:


def run_menu():
    # Asks user for first question on startup
    quest=input("Enter your question: ").strip()
    # Inference algorithm selections
    algo={
        "1": ("Chain of Thought",run_cot),
        "2": ("Self Consistency",run_scy),
        "3": ("Tree of Thought",run_tot),
        "4": ("Self-Refine",run_self_refine),
        "5": ("Analogical Reasoning",run_analogical),
        "6": ("Self-Debug",run_self_debug),
        "7": ("ReAct", run_react),
        "8": ("Decomposition",run_decomp),
        "9": ("Tool-Augmented Reasoning", run_tool_augmented)
    }
    while True:
        print("\nAvailable inference algorithms: ")
        for key,(name,_)in algo.items():
            print(f"{key},{name}")
        print("c. Change question")
        print("q. Quit")
        select=input("\nSelect one of the following options: ").strip().lower()
        # Quit menu
        if select=="q":
            print("Exiting tester...")
            break
        # Changes question
        if select=="c":
            quest=input("\nEnter a new question: ").strip()
            continue
        # Not valid option
        if select not in algo:
            print("Invalid selection, try again please...")
            continue
        # Running...
        name,func=algo[select]
        print(f"\nCurrently Running: {name}\n")
        print(func(quest))


# In[19]:


# Starts up the menu for user
run_menu()


# In[ ]:

