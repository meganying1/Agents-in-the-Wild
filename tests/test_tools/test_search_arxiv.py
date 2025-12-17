import os
import ast
import unittest
from smolagents import CodeAgent, FinalAnswerTool

from matvisor.llm import load_llama, SmolagentsAdapter
from matvisor.tools.search_arxiv import SearchArxiv
from matvisor.tools import LoggedTool
from matvisor.log import Logger


class TestSearchArxiv(unittest.TestCase):

    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        filename = "test_search_arxiv.jsonl"
        self.filepath = os.path.join(path, filename)

        # Remove old file if exists
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

        logger = Logger(self.filepath)

        parent_path = os.path.dirname(path)
        parent_path = os.path.dirname(parent_path)
        database_filepath = os.path.join(parent_path, "matvisor")
        database_filepath = os.path.join(database_filepath, "database")
        database_filepath = os.path.join(database_filepath, "database_test.csv")
        self.test_tool = SearchArxiv()  

        tools = [
            FinalAnswerTool(),
            self.test_tool,
        ]
        logged_tools = [LoggedTool(tool, logger) for tool in tools]

        system_prompt = """
        <|disable_thought|>You are an expert materials specialist. Use tools that you have and don't invent or try to access any tools that you don't have.
        """
        llama = load_llama("8")
        model = SmolagentsAdapter(llama, logger=logger)

        self.agent = CodeAgent(
            tools=logged_tools,
            instructions=system_prompt,
            model=model,
            add_base_tools=False,
            max_steps=5,
        )

    def tearDown(self):
        """
        Clean up the log file after test. Remove to keep logs for inspection.
        """
        if False:
            if os.path.exists(self.filepath):
                os.unlink(self.filepath)

    def test_search_arxiv(self):
        """
        Search for materials in the database with a mildly different input.
        """
        material_name = "Carbon Fiber?"
        expected_result = self.test_tool.forward(material_name)
        result = self.agent.run(f"What is {material_name} in summary. Provide your answer using final_answer only.")
        #print(result)

        # Test the logged result
        with open(self.filepath, "r") as f:
            lines = f.readlines()
            last_log = ast.literal_eval(lines[-1])
            #self.assertEqual(last_log["kind"], "tool_output")
            #self.assertEqual(last_log["tool"], "final_answer")


if __name__ == "__main__":
    unittest.main()