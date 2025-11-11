import os
import llama_cpp
from smolagents import CodeAgent, FinalAnswerTool

from matvisor.llm.smolagent_adaptor import SmolagentsAdapter
from matvisor.database import load_materials_from_file
from matvisor.log import Logger
from matvisor.tools import (
    SearchByMaterial,
)
from matvisor.tools import LoggedTool


path = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(path, "database")
filename = "database_test.csv"
filepath = os.path.join(database_path, filename)
df = load_materials_from_file(filepath)


def create_agent(
        llama_model: llama_cpp.Llama,
        system_prompt: str,
        fewshot_examples: list = None,
        max_steps: int = 10,
        logger: Logger | None = None
    ):

    def create_instructions(system_prompt, fewshot_examples):
        instructions = system_prompt
        if fewshot_examples is not None:
            instructions += "\n\nHere are some examples to help you:\n"
            for example in fewshot_examples:
                pass ####
        return instructions

    instructions = create_instructions(system_prompt, fewshot_examples)
    model = SmolagentsAdapter(llama_model, logger=logger)

    tools = [
        FinalAnswerTool(),
        SearchByMaterial(materials_df=df),
    ]

    if logger:
        # Add logging wrapper to all tools
        logged_tools = []
        for t in tools:
            logged_tools.append(LoggedTool(t, logger))
        tools = logged_tools

    return CodeAgent(
            tools=tools,
            model=model,
            instructions=instructions,
            add_base_tools=False,
            max_steps=max_steps,
            additional_authorized_imports=[],
        )


if __name__ == "__main__":

    from matvisor.llm import load_llama

    # Remove old file if exists
    log_path = os.path.join(path, "agent_log.jsonl")
    if os.path.exists(log_path):
        os.remove(log_path)

    llm = load_llama(modelsize="8")

    prompt = """
    You are an expert materials specialist. Use tools that you have and don't invent or try to access any tools that you don't have.
    """
    agent = create_agent(
        llama_model=llm,
        system_prompt=prompt,
        logger=Logger(path=log_path),
    )
    out = agent.run("What color is Terrazzoplatta?")
    print(out)