import llama_cpp
from smolagents.models import ChatMessage, MessageRole, Model
from matvisor.workshop.log import JSONLogger


qwen3_models = {
    "0.6": {
        "repo_id": "Qwen/Qwen3-0.6B-GGUF",
        "filename": "Qwen3-0.6B-Q8_0.gguf",
    },
    "1.7": {
        "repo_id": "Qwen/Qwen3-1.7B-GGUF",
        "filename": "Qwen3-1.7B-Q8_0.gguf",
    },
    "4": {
        "repo_id": "Qwen/Qwen3-4B-GGUF",
        "filename": "Qwen3-4B-Q8_0.gguf",
    },
    "8": {
        "repo_id": "Qwen/Qwen3-8B-GGUF",
        "filename": "Qwen3-8B-Q8_0.gguf",
    },
    "14": {
        "repo_id": "Qwen/Qwen3-14B-GGUF",
        "filename": "Qwen3-14B-Q8_0.gguf",
    },
    "32": {
        "repo_id": "Qwen/Qwen3-32B-GGUF",
        "filename": "Qwen3-32B-Q8_0.gguf",
    },
}

qwen3_models_list = list(qwen3_models.keys())

def load_llama(modelsize: str = "7") -> llama_cpp.Llama:
    models = qwen3_models
    #repo = f"bartowski/Qwen2.5-{modelsize}B-Instruct-GGUF"
    #filename=f"Qwen2.5-{modelsize}B-Instruct-Q4_K_M.gguf"
    #repo_id = f"Qwen/Qwen3-{modelsize}B-GGUF"
    #filename = f"Qwen3-{modelsize}B-Q8_0.gguf"
    return llama_cpp.Llama.from_pretrained(
        repo_id=models[modelsize]["repo_id"],
        filename=models[modelsize]["filename"],
        n_ctx=8192,
        #gpu=True,
        #metal=True,
        n_gpu_layers=-1,
        verbose=False,
    )


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


class LoggingSmolAdapter(_SmolAdapter):
    def __init__(self, llama_model, logger: JSONLogger):
        super().__init__(llama_model)
        self.logger = logger
        self.step = 0

    def _render(self, message):
        role = (getattr(message, "role", None) or message.get("role", "user")).upper()
        content = getattr(message, "content", None)
        if isinstance(message, dict):
            content = message.get("content")
        if isinstance(content, list):
            content = " ".join(
                part.get("text", str(part)) if isinstance(part, dict) else str(part)
                for part in content
            )
        return {"role": role, "content": content or ""}

    def generate(self, messages, stop_sequences=None, **kwargs):
        self.step += 1
        rendered_msgs = [self._render(m) for m in messages]
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in rendered_msgs) + "\nASSISTANT: "

        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "top_p": kwargs.get("top_p"),
            "max_tokens": kwargs.get("max_tokens", 512),
            "stop_sequences": stop_sequences,
        }

        # log request
        self.logger.log({
            "kind": "llm_request",
            "step": self.step,
            "messages": rendered_msgs,
            "prompt_preview": prompt[:5000],  # avoid giant lines if needed
            "params": {k: v for k, v in params.items() if v is not None},
        })

        r = self.llama.create_completion(
            prompt=prompt,
            stop=stop_sequences,
            **{k: v for k, v in params.items() if k != "stop_sequences" and v is not None}
        )
        text = r["choices"][0]["text"].strip()

        # log response
        self.logger.log({
            "kind": "llm_response",
            "step": self.step,
            "content": text,
            "raw": {"choices": [{"finish_reason": r["choices"][0].get("finish_reason")}], "usage": r.get("usage")},
        })

        return ChatMessage(role=MessageRole.ASSISTANT, content=text)


if __name__ == "__main__":

    messages=[
        {"role": "system", "content": "You are an expert materials science tutor."},
        {"role": "user", "content": "Explain what ductility means in less than five sentences."},
    ]

    llama = load_llama("0.6")

    # Without adapter
    response = llama.create_chat_completion(
        messages=messages,
        max_tokens=500,
        temperature=0.5
    )
    print(response["choices"][0]["message"]["content"])

    # With adapter
    adapter = _SmolAdapter(llama)
    reply = adapter.generate(
        messages=messages,
        max_tokens=200,
        temperature=0.5,
    )
    print(reply.content)
