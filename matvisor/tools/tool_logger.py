import time
from smolagents import Tool
from matvisor.log import Logger


class LoggedTool(Tool):

    def __init__(self, tool: Tool, logger: Logger):
        # Mirror the tool tool’s required attributes
        self.name = getattr(tool, "name", tool.__class__.__name__)
        self.description = getattr(tool, "description", "No description provided.")
        self.inputs = getattr(tool, "inputs", {})
        self.output_type = getattr(tool, "output_type", "any")

        # Keep references
        self.tool = tool
        self.logger = logger

        # CRITICAL: expose the tool forward (same signature!) before validation
        self.forward = tool.forward

        # Let smolagents validate now that attrs & forward are in place
        super().__init__()

    # Log around execution; delegate to the tool tool’s __call__
    def __call__(self, *args, **kwargs):

        # Log the tool inputs
        self.logger.log({
            "kind": "tool_call",
            "tool": self.tool.name,
            "args": args,
            "kwargs": kwargs,
        })

        start_time = time.time()

        result = self.tool(*args, **kwargs)

        duration = time.time() - start_time

        # Log the tool outputs
        self.logger.log({
            "kind": "tool_result",
            "tool": self.tool.name,
            "result": str(result),
            "duration": duration,
        })

        return result


if __name__ == "__main__":
    import os
    from smolagents import CodeAgent, FinalAnswerTool
    from smolagents.models import ChatMessage, MessageRole, Model

    from matvisor.llm import load_llama, SmolagentsAdapter

    path = os.path.dirname(os.path.abspath(__file__))
    filename = "tool_logger_test.jsonl"
    filepath = os.path.join(path, filename)

    # 1Remove old file if exists
    if os.path.exists(filepath):
        os.remove(filepath)

    logger = Logger(filepath)

    # <|disable_thought|> should be added to the system prompt to disable internal thoughts
    system_prompt = "<|disable_thought|>You are a mathematician assistant. Use tools to help answer user questions."
    llama = load_llama("0.6")
    model = SmolagentsAdapter(llama, logger=logger)
 
    class AddNumbers(Tool):
        name = "add_numbers"
        description = "Adds two numbers."
        # smolagents expects JSON-schema-like input spec
        inputs = {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        }
        output_type = "number"

        def forward(self, a: float, b: float) -> float:
            return a + b
    
    add_tool = AddNumbers()
    logged_add_tool = LoggedTool(add_tool, logger)
    final_answer_tool = FinalAnswerTool()
    logged_final_answer_tool = LoggedTool(final_answer_tool, logger)
    agent = CodeAgent(
        tools=[logged_add_tool, logged_final_answer_tool],
        instructions=system_prompt,
        model=model,
        add_base_tools=False,
        max_steps=2,
    )
    # Ask the agent to do something that should trigger the tool
    result = agent.run("Please add 2 and 3 using the tool. Only report the final result with final_answer.")

    # Remove log file after test
    #os.remove(filepath)