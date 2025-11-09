# models_llama.py
import os
from smolagents import Model, ChatMessage, TokenUsage

# Optional: only import llama_cpp when needed (keeps fast tests snappy)
_llama_available = False
try:
    import llama_cpp
    _llama_available = True
except Exception:
    pass


class FakeModel(Model):
    def __init__(self, prefix="[FAKE] "):
        self.prefix = prefix

    def generate(self, messages, stop_sequences=None, response_format=None, grammar=None, **kwargs):
        # Return content that the current CodeAgent parser accepts:
        # needs a code block and a final_answer(...) call, ending with <end_action>.
        content = (
            "Thought: I will write a tiny code block that prints hello and then calls final_answer.\n"
            "<code>\n"
            "print('hello')\n"
            "final_answer('done')\n"
            "</code>\n"
            "<end_action>"
        )
        return ChatMessage(role="assistant", content=content, token_usage=TokenUsage(input_tokens=1, output_tokens=5))


class LlamaCppModel(Model):

    def __init__(self, llm):
        self.llm = llm

    @staticmethod
    def _coerce_content(content):
        """llama.cpp chat template expects a string; smolagents may pass lists/dicts.
        Convert lists to a single string and dicts to JSON.
        """
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        # If content is a list (e.g., mixed strings, dicts), stringify items and join with newlines
        if isinstance(content, list):
            try:
                return "\n".join(
                    [c if isinstance(c, str) else __import__("json").dumps(c, ensure_ascii=False) for c in content]
                )
            except Exception:
                return str(content)
        # Fallback: dict or other types -> JSON or str
        try:
            import json
            return json.dumps(content, ensure_ascii=False)
        except Exception:
            return str(content)

    def generate(self, messages, stop_sequences=None, response_format=None, grammar=None, **kwargs):
        # Normalize message objects (dict or ChatMessage) to {"role": str, "content": str}
        norm_messages = []
        for m in messages:
            if isinstance(m, dict):
                role = m.get("role", "user")
                content = self._coerce_content(m.get("content", ""))
            else:
                # Support smolagents ChatMessage objects (attributes access)
                role = getattr(m, "role", "user")
                content = self._coerce_content(getattr(m, "content", ""))
            norm_messages.append({"role": role, "content": content})

        resp = self.llm.create_chat_completion(
            messages=norm_messages,
            stop=stop_sequences,
            max_tokens=kwargs.get("max_tokens", 512),
            temperature=kwargs.get("temperature", 0.4),
        )
        content = resp["choices"][0]["message"].get("content", "")
        usage = resp.get("usage") or {}
        return ChatMessage(
            role="assistant",
            content=content,
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
        n_ctx=8192,  # 2048
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
        print("  ->", (msg.content or "")[:120], "...")