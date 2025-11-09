import llama_cpp
from smolagents.models import ChatMessage, MessageRole, Model

from matvisor.workshop.log import Logger


class SmolagentsAdapter(Model):
    def __init__(self, llama_model: llama_cpp.Llama, logger: Logger = None):
        super().__init__()
        self.llama = llama_model
        self.logger = logger
        self.step = 0

    def generate(self, messages, stop_sequences=None, **kwargs) -> ChatMessage:
        # Normalize incoming messages (dicts or ChatMessage) to llama_cpp chat format

        llama_messages = []
        for m in messages:
            if isinstance(m, ChatMessage):
                # m.role is a MessageRole enum in smolagents
                role = m.role.value if isinstance(m.role, MessageRole) else m.role
                content = m.content
            else:
                role = m.get("role", "user")
                content = m.get("content", "")
            llama_messages.append({"role": role, "content": content})

        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "top_p": kwargs.get("top_p"),
            "max_tokens": kwargs.get("max_tokens", 512),
        }
        params = {k: v for k, v in params.items() if v is not None}

        if stop_sequences:
            params["stop"] = stop_sequences

        # Log system prompt
        if self.step == 0 and self.logger:
            system_prompt = llama_messages[0]["content"] if llama_messages else ""
            self.logger.log({
                "kind": "llm_system_pprompt",
                "step": self.step,
                "system_prompt": system_prompt,
            })

        self.step += 1

        # Use chat completion API correctly: no 'prompt', pass messages=
        response = self.llama.create_chat_completion(
            messages=llama_messages,
            **params,
        )

        content = response["choices"][0]["message"]["content"]
        # Clean the output by removing any <think> tags if present
        content = content.replace("<think>\n\n</think>\n\n", "").replace("<think>\n</think>\n\n", "")
        
        # Log input and output
        if self.logger:
            latest_input = llama_messages[-1]["content"] if llama_messages else ""
            self.logger.log({
                "kind": "llm_request",
                "step": self.step,
                "input": latest_input,
                "output": content,
            })

        return ChatMessage(role=MessageRole.ASSISTANT, content=content)
    

if __name__ == "__main__":

    from matvisor.workshop.llm.llama import load_llama

    # <|disable_thought|> should be added to the system prompt to disable internal thoughts
    messages=[
        {"role": "system", "content": "<|disable_thought|>You are an expert materials science tutor."},
        {"role": "user", "content": "Explain what ductility means in less than five sentences."},
    ]
    llama = load_llama("0.6")
    adapter = SmolagentsAdapter(llama, logger=Logger())
    reply = adapter.generate(
        messages=messages,
        max_tokens=200,
        temperature=0.5,
    )
    print(reply.content)