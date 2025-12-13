import os
import ast
import unittest
from smolagents import CodeAgent, FinalAnswerTool

from matvisor.llm import load_llama, SmolagentsAdapter
from matvisor.tools.tool_test import AddNumbers
from matvisor.tools import LoggedTool
from matvisor.log import Logger


class TestToolLogging(unittest.TestCase):
    
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        filename = "logged_tool_test.jsonl"
        self.filepath = os.path.join(path, filename)

        # Remove old file if exists
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

        logger = Logger(self.filepath)

        self.add_numbers_tool = AddNumbers()    
        
        tools = [
            FinalAnswerTool(),
            self.add_numbers_tool,
        ]
        logged_tools = [LoggedTool(tool, logger) for tool in tools]

        system_prompt = "<|disable_thought|>You are a mathematician assistant. Use tools to help answer user questions."
        llama = load_llama("0.6")
        model = SmolagentsAdapter(llama, logger=logger)

        self.agent = CodeAgent(
            tools=logged_tools,
            instructions=system_prompt,
            model=model,
            add_base_tools=False,
            max_steps=2,
        )

    def tearDown(self):
        """
        Clean up the log file after test. Remove to keep logs for inspection.
        """
        if True:
            if os.path.exists(self.filepath):
                os.unlink(self.filepath)

    def test_tool_logging(self):
        expected_result = self.add_numbers_tool.forward(2, 3)
        result = self.agent.run("Please add 2 and 3 using the tool. Only report the final result with final_answer.")
        # Test the raw result
        self.assertEqual(result, expected_result)
        # Test the logged result
        with open(self.filepath, "r") as f:
            lines = f.readlines()
            last_log = ast.literal_eval(lines[-1])
            self.assertEqual(last_log["kind"], "tool_output")
            self.assertEqual(last_log["tool"], "final_answer")
            self.assertEqual(last_log["output"], expected_result)


if __name__ == "__main__":
    unittest.main()