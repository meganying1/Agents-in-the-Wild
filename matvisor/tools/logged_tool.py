"""
A wrapper around smolagents Tool that logs tool calls and results.

* Log entries for a tool call have the following structure:
    {
        "kind": "tool_input",
        "tool": <tool name>,
        "args": <args>,
        "kwargs": <kwargs>,
        "time": <time in %Y-%m-%d %H:%M:%S format>,
    }
* Log entries for a tool result have the following structure:
    {
        "kind": "tool_output",
        "tool": <tool name>,
        "output": <tool result>,
        "duration": <duration in seconds>,
        "time": <time in %Y-%m-%d %H:%M:%S format>,
    }
"""

from datetime import datetime
from smolagents import Tool

from matvisor.log import Logger


class LoggedTool(Tool):
    """
    Accepts any smolagents Tool and a Logger instance and wraps the tool to log its calls and results.
    """
    def __init__(self, tool: Tool, logger: Logger = None):
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

    def __call__(self, *args, **kwargs):
        """
        Log around execution; delegate to the tool tool’s __call__ method.
        """
        # Log the tool inputs
        if self.logger:
            start_time = datetime.now()  # Start time for logging
            self.logger.log({
                "kind": "tool_input",
                "tool": self.tool.name,
                "args": args,
                "kwargs": kwargs,
                "time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        # Actual tool execution
        result = self.tool(*args, **kwargs)

        # Log the tool outputs
        if self.logger:
            end_time = datetime.now()  # End time for logging
            duration = end_time - start_time
            self.logger.log({
                "kind": "tool_output",
                "tool": self.tool.name,
                "output": result,
                "duration": duration.total_seconds(),
                "time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return result


if __name__ == "__main__":

    import os
    from smolagents import CodeAgent, FinalAnswerTool

    from matvisor.llm import load_llama, SmolagentsAdapter

    path = os.path.dirname(os.path.abspath(__file__))
    filename = "tool_logger_test.jsonl"
    filepath = os.path.join(path, filename)

    # Remove old file if exists
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
        inputs = {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        }
        output_type = "number"

        def forward(self, a: float, b: float) -> float:
            return a + b
    
    tools = [AddNumbers(), FinalAnswerTool()]
    logged_tools = [LoggedTool(tool, logger) for tool in tools]

    agent = CodeAgent(
        tools=logged_tools,
        instructions=system_prompt,
        model=model,
        add_base_tools=False,
        max_steps=2,
    )

    result = agent.run("Please add 2 and 3 using the tool. Only report the final result with final_answer.")

    # Remove log file after test
    #os.remove(filepath)