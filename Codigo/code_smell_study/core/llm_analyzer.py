# code_smell_study/core/llm_analyzer.py
import os
import json
import time
import openai
import tiktoken
import re

from config.settings import MODEL, MAX_TOKENS, SYSTEM_PROMPT, PROMPT_TEMPLATE
from openai.error   import RateLimitError

# configura a chave
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Defina OPENAI_API_KEY em config/.env")

def count_tokens(text: str, model: str = MODEL) -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def split_into_chunks(code: str) -> list[str]:
    parts = re.split(r"(?m)^(class\s+\w+|def\s+\w+)", code)
    chunks: list[str] = []

    if len(parts) > 1:
        head = parts[0]
        if head.strip():
            chunks.append(head)
        for i in range(1, len(parts), 2):
            header, body = parts[i], parts[i+1]
            chunks.append(header + body)
    else:
        chunks = [code]

    final: list[str] = []
    for chunk in chunks:
        if count_tokens(chunk) <= MAX_TOKENS:
            final.append(chunk)
        else:
            temp = ""
            for line in chunk.splitlines(keepends=True):
                if count_tokens(temp + line) > MAX_TOKENS:
                    final.append(temp)
                    temp = line
                else:
                    temp += line
            if temp:
                final.append(temp)
    return final

def analyze_with_llm(code_chunk: str) -> dict:
    # monta mensagens
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": PROMPT_TEMPLATE.format(code=code_chunk)}
    ]
    backoff = 1

    while True:
        try:
            resp = openai.ChatCompletion.create(
                model=MODEL,
                messages=messages,
                temperature=0.0,
            )
            return json.loads(resp.choices[0].message.content)
        except RateLimitError:
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
        except json.JSONDecodeError:
            return {
                "error": "invalid_json",
                "raw": resp.choices[0].message.content
            }
