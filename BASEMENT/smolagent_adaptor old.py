import llama_cpp
from smolagents.models import ChatMessage, MessageRole, Model


class _SmolAdapter(Model):
    def __init__(self, llama_model: llama_cpp.Llama):
        super().__init__()
        self.llama = llama_model

    def generate(self, messages, stop_sequences=None, **kwargs):
        def render(message):
            role = (getattr(message, "role", None) or message.get("role", "user")).upper()
            content = getattr(message, "content", None)
            if isinstance(message, dict):
                content = message.get("content")
            if isinstance(content, list):
                content = " ".join(
                    part.get("text", str(part)) if isinstance(part, dict) else str(part) for part in content
                )
            return f"{role}: {content or ''}"

        prompt = "\n".join(render(m) for m in messages) + "\nASSISTANT: "
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "top_p": kwargs.get("top_p"),
            "max_tokens": kwargs.get("max_tokens", 512),
        }
        r = self.llama.create_completion(prompt=prompt, stop=stop_sequences, **{k: v for k, v in params.items() if v is not None})
        return ChatMessage(role=MessageRole.ASSISTANT, content=r["choices"][0]["text"].strip())
    

if __name__ == "__main__":

    from matvisor.workshop.llm.llama import load_llama

    # <|disable_thought|> should be added to the system prompt to disable internal thoughts
    messages=[
        {"role": "system", "content": "<|disable_thought|>You are an expert materials science tutor."},
        {"role": "user", "content": "Explain what ductility means in less than five sentences."},
    ]
    llama = load_llama("0.6")
    adapter = _SmolAdapter(llama)
    reply = adapter.generate(
        messages=messages,
        max_tokens=200,
        temperature=0.5,
    )
    print(reply.content)