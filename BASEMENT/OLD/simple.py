import llama_cpp
from smolagents.models import ChatMessage, MessageRole, Model
from smolagents import CodeAgent, FinalAnswerTool, Tool


def load_llama(modelsize: str = "4") -> llama_cpp.Llama:
    return llama_cpp.Llama.from_pretrained(
        repo_id=f"bartowski/Qwen_Qwen3-{modelsize}B-Instruct-2507-GGUF",
        filename=f"Qwen_Qwen3-{modelsize}B-Instruct-2507-Q4_K_M.gguf",
        n_ctx=8192,
        gpu=True,
        metal=True,
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

class AddTwoNumbersTool(Tool):
    name = "add_two_numbers"
    description = "Adds two numbers and returns their sum."
    inputs = {
        "a": {"type": "number", "description": "First addend"},
        "b": {"type": "number", "description": "Second addend"},
    }
    output_type = "number"
    
    def forward(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

def create_agent(
        llm,
        system_prompt: str,
    ):
    instructions = system_prompt
    tools = [
        FinalAnswerTool(),
        AddTwoNumbersTool(),
    ]
    return CodeAgent(
            tools=tools,
            model=llm,
            instructions=instructions,
            add_base_tools=False,
            max_steps=3,
            additional_authorized_imports=[],
        )

teacher_system_prompt = """
Your a teacher that creates a detailed lesson to teach a novice how to use and not use a tool.
Try to create a comprehensive lesson and cover all important aspects of using the tool.
In the final step or when you are done, return your lesson material in the code block with final_answer tag.
"""

#teacher_llm = load_llama(modelsize="4")
#teacher_model = _SmolAdapter(teacher_llm)
#teacher_agent = create_agent(llm=teacher_model, system_prompt=teacher_system_prompt)
#out = teacher_agent.run("Teach me how to use the add_two_numbers tool.")
#print(out)

example_out = """
The add_two_numbers tool is used to add exactly two numbers. It takes two numeric inputs (integers or floats) and returns their sum. It should not be used for operations involving more than two numbers or for non-addition operations like multiplication, division, or exponentiation. For complex additions, break the problem into smaller steps or use alternative methods. Always ensure inputs are valid numbers.
"""
auditor_system_prompt = """
You inspect the provided tutorial by the teacher for logic gaps, wrong assumptions, edge-case omissions, and ambiguity and provide a report. Here is the tutorial to inspect:
"""
auditor_llm = load_llama(modelsize="4")
auditor_model = _SmolAdapter(auditor_llm)
auditor_agent = create_agent(llm=auditor_model, system_prompt=auditor_system_prompt)
out = auditor_agent.run(example_out)
print(out)