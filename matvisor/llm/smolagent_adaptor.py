"""
An adaptor to use smolagents models with the LLM interface.
When provided a Logger instance, logs LLM interactions in the following format:

* Log entries for system prompts have the following structure:
    {
        "kind": "llm_system_prompt",
        "system_prompt": <system prompt content>,
    }
* Log entries for the llm call have the following structure:
    {
        "kind": "llm_input",
        "step": <step>,
        "input": <llm input content>,
        "time": <time in %Y-%m-%d %H:%M:%S format>,
    }
* Log entries for the llm output have the following structure:
    {
        "kind": "llm_output",
        "step": <step>,
        "output": <llm output content>,
        "duration": <duration in seconds>,
        "time": <time in %Y-%m-%d %H:%M:%S format>,
    }
"""

import re
from datetime import datetime
import llama_cpp
from smolagents.models import ChatMessage, MessageRole, Model

from matvisor.log import Logger


class SmolagentsAdapter(Model):

    def __init__(self, llama_model: llama_cpp.Llama, logger: Logger = None):
        super().__init__()
        self.llama = llama_model
        self.logger = logger
        self.step = 1

    def _normalize_content(self, content):
        """
        Normalize the content of a message to a string.
        """
        # If it's already a string, done
        if isinstance(content, str):
            return content

        # If it's a list (e.g. multi-part messages), join sensibly
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict):
                    # Common pattern: {"type": "text", "text": "..."}
                    if "text" in part:
                        parts.append(str(part["text"]))
                    else:
                        parts.append(str(part))
                else:
                    parts.append(str(part))
            return " ".join(parts)

        # Fallback: just cast to string
        return str(content)

    def generate(self, messages, stop_sequences=None, **kwargs) -> ChatMessage:
        # Normalize incoming messages (dicts or ChatMessage) to llama_cpp chat format

        llama_messages = []
        for m in messages:
            # smolagents may give ChatMessage or dict-like
            if isinstance(m, ChatMessage):
                role = m.role.value if isinstance(m.role, MessageRole) else m.role
                content = m.content
            else:
                role = m.get("role", "user")
                content = m.get("content", "")

            content = self._normalize_content(content)
            llama_messages.append({"role": role, "content": content})


        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "top_p": kwargs.get("top_p"),
            "max_tokens": kwargs.get("max_tokens", 512),
        }
        params = {k: v for k, v in params.items() if v is not None}

        if stop_sequences:
            params["stop"] = stop_sequences

        if self.logger:
            # Log the LLM system prompt
            if self.step == 1:
                system_prompt = llama_messages[0]["content"] if llama_messages else ""
                self.logger.log({
                    "kind": "llm_system_prompt",
                    "system_prompt": system_prompt,
                })
            # Log the LLM input
            start_time = datetime.now()  # Start time for logging
            latest_input = llama_messages[-1]["content"] if llama_messages else ""
            self.logger.log({
                "kind": "llm_input",
                "step": self.step,
                "input": latest_input,
                "time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        # Use chat completion API correctly: no 'prompt', pass messages=
        response = self.llama.create_chat_completion(
            messages=llama_messages,
            **params,
        )

        content = response["choices"][0]["message"]["content"]
        
        # Clean the output by removing any empty <think> tags if present
        #content = content.replace("<think>\n\n</think>\n\n", "").replace("<think>\n</think>\n\n", "")
        # Clean the outout by removing any <think> blocks
        content = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL).strip()
        
        # Log the LLM output
        if self.logger:
            end_time = datetime.now()  # End time for logging
            duration = end_time - start_time
            latest_input = llama_messages[-1]["content"] if llama_messages else ""
            self.logger.log({
                "kind": "llm_output",
                "step": self.step,
                "output": content,
                "duration": duration.total_seconds(),
                "time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        self.step += 1

        return ChatMessage(role=MessageRole.ASSISTANT, content=content)
    

if __name__ == "__main__":

    import os

    from matvisor.llm.llama import load_llama

    path = os.path.dirname(os.path.abspath(__file__))
    filename = "smolagent_adaptor_test.jsonl"
    filepath = os.path.join(path, filename)

    # Remove old file if exists
    if os.path.exists(filepath):
        os.remove(filepath)

    logger = Logger(filepath)

    # <|disable_thought|> should be added to the system prompt to disable internal thoughts
    messages=[
        {"role": "system", "content": "<|disable_thought|>You are an expert materials science tutor."},
        {"role": "user", "content": "Explain what ductility means in less than five sentences."},
    ]
    llama = load_llama("0.6")
    adapter = SmolagentsAdapter(llama, logger=logger)
    reply = adapter.generate(
        messages=messages,
        max_tokens=200,
        temperature=0.5,
    )
    print(reply.content)