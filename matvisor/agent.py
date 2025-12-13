import os
import llama_cpp
from smolagents import CodeAgent, FinalAnswerTool

from matvisor.default_system_prompt import DEFAULT_SYSTEM_PROMPT
from matvisor.llm.smolagent_adaptor import SmolagentsAdapter
from matvisor.database import load_materials_from_file
from matvisor.log import Logger
from matvisor.tools import (
    SearchByMaterial,
)
from matvisor.tools import LoggedTool


def create_instructions(system_prompt: str | None = None, fewshot_examples: list | None = None, thinking: bool = False):
    """
    Create agent instructions with optional few-shot examples and thinking control.
    """
    instructions = ""
    if thinking is False:
        instructions += "<|disable_thought|>"
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    instructions += system_prompt
    if fewshot_examples is not None:
        instructions += "\n\nHere are some examples to help you:\n"
        for example in fewshot_examples:
            pass ####
    return instructions

def create_agent(
        path: str,
        llama_model: llama_cpp.Llama,
        system_prompt: str = "",
        fewshot_examples: list = None,
        max_steps: int = 10,
        database_filename: str = "database.csv",
        log_filename: str = "log.jsonl",
        reset_log: bool = True,
    ):
    """
    Create a smolagent CodeAgent with tools and logging capabilities.
    """
    log_filepath = os.path.join(path, log_filename)
    logger = Logger(log_filepath)

    if reset_log and os.path.exists(log_filepath):
        os.remove(log_filepath)

    database_filepath = os.path.join(path, database_filename)
    df = load_materials_from_file(database_filepath)

    instructions = create_instructions(system_prompt, fewshot_examples)
    model = SmolagentsAdapter(llama_model, logger=logger)

    tools = [
        FinalAnswerTool(),
        SearchByMaterial(materials_df=df),
    ]

    # Add logging to tools
    logged_tools = []
    for t in tools:
        logged_tools.append(LoggedTool(t, logger))

    return CodeAgent(
            tools=logged_tools,
            model=model,
            instructions=instructions,
            add_base_tools=False,
            max_steps=max_steps,
            additional_authorized_imports=[],
        )


if __name__ == "__main__":

    from matvisor.llm import load_llama

    path = os.path.dirname(os.path.abspath(__file__))
    database_filename = os.path.join("database", "database_test.csv")
    llm = load_llama(modelsize="8")
    system_prompt = """
    You are an expert materials specialist. Use tools that you have and don't invent or try to access any tools that you don't have.
    """
    agent = create_agent(
        path=path,
        llama_model=llm,
        system_prompt=system_prompt,
        database_filename=database_filename,
    )
    out = agent.run("Which country produces Terrazzoplatta?")
    print(out)

    #os.remove(os.path.join(path, "log.jsonl"))