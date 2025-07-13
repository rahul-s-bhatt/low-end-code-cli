# File: src/model.py
from llama_cpp import Llama
import os

class LocalModel:
    def __init__(self):
        model_path = "models/Phi-3-mini-4k-instruct-q4.gguf"
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )

    def complete_code(self, context):
        prompt = f"Complete this Python code:\n\n{context}\n\nCOMPLETION:"
        response = self.llm(prompt, max_tokens=80, stop=["\n\n", "```"])
        return response['choices'][0]['text'].strip()

    def explain_code(self, code):
        prompt = f"Explain this Python code briefly:\n\n{code}\n\nEXPLANATION:"
        response = self.llm(prompt, max_tokens=100)
        return response['choices'][0]['text'].strip()
