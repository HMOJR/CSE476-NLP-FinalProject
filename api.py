#!/usr/bin/env python
# coding: utf-8

# In[5]:


# LLM wrapper for inference technique testing by Hector Orozco

import requests
import os


# In[7]:


API_KEY=os.getenv("OPENAI_API_KEY")
if not API_KEY:
    API_KEY=input("Enter your LLM API Key to get started: ").strip()
API_BASE="https://openai.rc.asu.edu/v1"
MODEL_NAME=os.getenv("MODEL_NAME")
if not MODEL_NAME:
    MODEL_NAME=input("Enter model name: ").strip()
    
def llm_caller(prompt,sys="",temp=0.0,mod=None):
    if mod is None:
        mod=MODEL_NAME
    url=f"{API_BASE}/chat/completions"
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload={
        "model": mod,
        "messages": [
            {"role": "system","content": sys},
            {"role": "user","content": prompt},
        ],
        "temperature": temp,
        "max_tokens": 1024,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)

    # handles potential crashes
    if resp.status_code != 200:
        return ""

    try:
        return resp.json()["choices"][0]["message"]["content"]
    except:
        return ""


# In[ ]:




