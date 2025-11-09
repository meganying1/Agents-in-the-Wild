class MinimalChatModel:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, messages, **kwargs):
        # messages: list of {"role": "...", "content": "..."}
        resp = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 256),
            temperature=kwargs.get("temperature", 0.4),
        )
        return resp["choices"][0]["message"].get("content", "")
    
from matvisor.models_llama import load_llama

llm = load_llama("7")
model = MinimalChatModel(llm)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Name one heat-resistant grip material for kitchen utensils and why."},
]
print(model.generate(messages))