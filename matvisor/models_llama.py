# models_llama.py
import os
from smolagents import Model

# Optional: only import llama_cpp when needed (keeps fast tests snappy)
_llama_available = False
try:
    import llama_cpp
    _llama_available = True
except Exception:
    pass


class TokenUsage:
    def __init__(self, input_tokens: int = 0, output_tokens: int = 0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens


class SimpleMessage:
    def __init__(self, content: str, token_usage: TokenUsage | None = None):
        self.content = content
        self.token_usage = token_usage or TokenUsage()


class FakeModel(Model):
    def __init__(self, prefix="[FAKE] "):
        self.prefix = prefix

    def generate(self, messages, stop_sequences=None, grammar=None, **kwargs):
        # Return content that the current CodeAgent parser accepts:
        # needs a <code>...</code> block and a final_answer(...) call.
        content = (
            "Thought: I will write a tiny code block that prints hello and then calls final_answer.\n"
            "<code>\n"
            "print('hello')\n"
            "final_answer('done')\n"
            "</code>"
        )
        return SimpleMessage(content, token_usage=TokenUsage(1, 5))


class LlamaCppModel(Model):
    def __init__(self, llm):
        self.llm = llm

    def generate(self, messages, stop_sequences=None, grammar=None, **kwargs):
        resp = self.llm.create_chat_completion(
            messages=messages,
            stop=stop_sequences,
            max_tokens=kwargs.get("max_tokens", 512),
            temperature=kwargs.get("temperature", 0.4),
        )
        content = resp["choices"][0]["message"]["content"]
        usage = resp.get("usage") or {}
        return SimpleMessage(
            content,
            token_usage=TokenUsage(
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
            ),
        )
    

def load_llama(modelsize="7"):
    """
    Helper: build a llama_cpp.Llama object (heavy).
    """
    if not _llama_available:
        raise RuntimeError("llama_cpp not installed in this env.")
    return llama_cpp.Llama.from_pretrained(
        repo_id=f"bartowski/Qwen2.5-{modelsize}B-Instruct-GGUF",
        filename=f"Qwen2.5-{modelsize}B-Instruct-Q4_K_M.gguf",
        n_ctx=2048,
        gpu=True,
        metal=True,
        n_gpu_layers=-1
    )


if __name__ == "__main__":
    # Fast test first
    print("[models_llama] Testing FakeModel...")
    fm = FakeModel()
    msg = fm.generate([{"role": "user", "content": "hello"}])
    print("  ->", msg.content)

    # Optional heavy test
    if os.environ.get("RUN_LLAMA") == "1":
        print("[models_llama] Loading llama.cpp model (heavy)...")
        llm = load_llama("7")
        model = LlamaCppModel(llm)
        msg = model.generate([{"role": "user", "content": "Say hi"}])
        print("  ->", msg.content[:120], "...")