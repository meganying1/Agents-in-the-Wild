import llama_cpp


def load_llama(modelsize="7"):
    """
    Helper: build a llama_cpp.Llama object (heavy).
    """
    return llama_cpp.Llama.from_pretrained(
        repo_id=f"bartowski/Qwen2.5-{modelsize}B-Instruct-GGUF",
        filename=f"Qwen2.5-{modelsize}B-Instruct-Q4_K_M.gguf",
        n_ctx=8192,  # 2048
        gpu=True,
        metal=True,
        n_gpu_layers=-1,
        verbose=False,
    )

llm = load_llama(modelsize="7")

if False:
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are an expert materials science tutor."},
            {"role": "user", "content": "Explain what ductility means in less than 5 sentences."}
        ],
        max_tokens=500,
        temperature=0.5
    )

    print(response["choices"][0]["message"]["content"])


class Chat:
    
    def __init__(self, llm, system_prompt: str):
        self.llm = llm
        self.conversation = [
            {"role": "system", "content": system_prompt},
        ]

    def send_message(self, message: str) -> str:
        self.conversation.append({"role": "user", "content": message})
        response = llm.create_chat_completion(
                messages=self.conversation,
                max_tokens=500,
                temperature=0.5
            )
        result = response["choices"][0]["message"]["content"]
        self.conversation.append({"role": "assistant", "content": result})
        return result

if False:
    chat = Chat(llm, system_prompt="You are an expert materials science tutor.")
    response = chat.send_message("Explain what ductility means in less than 5 sentences.")
    print(response)

    response = chat.send_message("Explain how it is measured.")
    print(response)


class _SmolAdapter:
    def __init__(self, llama): self.llama = llama
    def generate(self, messages, stop_sequences=None, **kwargs):
        temperature = kwargs.get("temperature", 0.2)
        max_tokens  = kwargs.get("max_tokens", 512)
        if hasattr(self.llama, "create_chat_completion"):
            r = self.llama.create_chat_completion(
                messages=messages, temperature=temperature,
                max_tokens=max_tokens, stop=stop_sequences
            )
            return r["choices"][0]["message"]["content"]
        # Fallback for very old llama_cpp builds:
        prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages) + "\nASSISTANT: "
        r = self.llama.create_completion(
            prompt=prompt, temperature=temperature,
            max_tokens=max_tokens, stop=stop_sequences
        )
        return r["choices"][0]["text"]


from smolagents import CodeAgent, FinalAnswerTool

agent = CodeAgent(
        tools=[FinalAnswerTool()],
        model=llm,
        instructions="You are an expert materials science tutor.",
        add_base_tools=False,
        max_steps=10,
        additional_authorized_imports=[],
    )

out = agent.run("What is density?")