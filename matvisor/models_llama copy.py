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
        # needs a Markdown code block and a final_answer(...) call, ending with <end_action>.
        content = (
            "Thought: I will write a tiny code block that prints hello and then calls final_answer.\n"
            "```py\n"
            "print('hello')\n"
            "final_answer('done')\n"
            "```<end_action>"
        )
        return SimpleMessage(content, token_usage=TokenUsage(1, 5))


class LlamaCppModel(Model):
    def _convert_markdown_codeblocks(self, text: str) -> str:
        """
        Convert Markdown fenced code blocks (``` ... ```) into <code>...</code> blocks
        so that smolagents' CodeAgent parser (which expects <code>...</code>) accepts them.
        We support ```py, ```python, and plain ``` fences.
        """
        import re

        # Normalize Windows newlines to \n for regex simplicity
        s = text.replace("\r\n", "\n").replace("\r", "\n")

        # Regex to capture fenced blocks with an optional language tag.
        pattern = re.compile(r"```(?:py|python)?\n(.*?)```", re.DOTALL | re.IGNORECASE)

        def _repl(m: re.Match) -> str:
            inner = m.group(1)
            # Strip a single leading/trailing newline if present to keep things tidy
            if inner.startswith("\n"):
                inner = inner[1:]
            if inner.endswith("\n"):
                inner = inner[:-1]
            return f"&lt;code&gt;\n{inner}\n&lt;/code&gt;"

        s = pattern.sub(_repl, s)

        # Also handle inline single-line fenced snippets like ```print(1)```
        inline_pattern = re.compile(r"```(.*?)```", re.DOTALL)
        s = inline_pattern.sub(lambda m: f"&lt;code&gt;{m.group(1)}&lt;/code&gt;", s)

        # Replace HTML-escaped tags back to real ones
        s = s.replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>")
        return s

    def _patch_action_format(self, text: str) -> str:
        """
        Make the model output acceptable to smolagents' CodeAgent parser:
        - remove any stray <end_action> markers from inside content
        - convert Markdown fences to <code>…</code> (via _convert_markdown_codeblocks)
        - if there's a stray closing </code>, remove it
        - if there is still no <code> block, try to extract code after a 'Code:' section or a final_answer(...) call
        - as a last resort, wrap the whole text into final_answer('...') to produce a valid action
        - ensure the '<end_action>' terminator is present outside </code>
        """
        import re

        # Start with a safe string
        s = (text or "").replace("\r\n", "\n").replace("\r", "\n")

        # 0) Strip any stray <end_action> early so it cannot end up inside the code block
        s = s.replace("<end_action>", "")

        # 1) Convert markdown code blocks if any
        s = self._convert_markdown_codeblocks(s)

        # 2) Fix orphan closing tag (model sometimes emits a bare </code>)
        if "</code>" in s and "<code>" not in s:
            s = s.replace("</code>", "").strip()

        # 3) If we still don't have a code block, construct one
        if "<code>" not in s:
            # Try to capture code after "Code:" up to ``` or end
            m = re.search(r"(?is)Code:\s*(?:```(?:py|python)?\n)?(.*?)(?:```|$)", s)
            if m and m.group(1).strip():
                block = m.group(1).strip()
            else:
                # Try to salvage an existing final_answer(...) call
                m2 = re.search(r"final_answer\s*\([^)]*\)", s, flags=re.IGNORECASE | re.DOTALL)
                if m2:
                    block = m2.group(0).strip()
                else:
                    # Last resort: wrap the entire message as a final answer string
                    safe = s.strip().replace("\\", "\\\\").replace("\n", "\\n").replace("'", "\\'")
                    block = f"final_answer('{safe}')"
            s = f"<code>\n{block}\n</code>"

        # 4) Ensure the terminator exists and is OUTSIDE the </code> block
        s = s.rstrip()
        if not s.endswith("</code>"):
            # If the model somehow didn't close the code block, force-close
            s = s + ("\n" if not s.endswith("\n") else "") + "</code>"
        # Append end marker on a new line for clarity
        s = s + "\n<end_action>"

        return s
    def __init__(self, llm):
        self.llm = llm

    def _coerce_content(self, content):
        """Ensure chat message content is a plain string for gguf chat templates."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict):
                    if "text" in p:
                        parts.append(str(p.get("text", "")))
                    elif "content" in p:
                        parts.append(str(p.get("content", "")))
                    else:
                        parts.append(str(p))
                else:
                    parts.append(str(p))
            return "\n".join(parts)
        if isinstance(content, dict):
            if "text" in content:
                return str(content.get("text", ""))
            if "content" in content:
                return str(content.get("content", ""))
            return str(content)
        return str(content)

    def generate(self, messages, stop_sequences=None, grammar=None, **kwargs):
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
        content = self._patch_action_format(content)
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
        print("  ->", msg.content[:120], "...")