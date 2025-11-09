import os
from smolagents import CodeAgent, FinalAnswerTool
from matvisor.workshop.llm.smolagent_adaptor import LoggingSmolAdapter
from matvisor.workshop.log import JSONLogger
from matvisor.workshop.tools.tool_logger import LoggedTool
from matvisor.workshop.tools.final_answer import LoggedFinalAnswerTool
from matvisor.workshop.database.material_search import SearchByMaterial
from matvisor.workshop.database.load_file import load_materials_from_file

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, "database")
filename = "AEC Material Database - Sheet1.csv"
filepath = os.path.join(path, filename)
df = load_materials_from_file(filepath)


def create_agent(
        llm,
        system_prompt: str,
        few_shot_examples: list = None, ####
        logger: JSONLogger | None = None
    ):
    instructions = system_prompt
    if few_shot_examples:
        instructions += "\n\nHere are some examples to help you:\n"
        for example in few_shot_examples:
            pass ####
    
    tools = [
        FinalAnswerTool(),
        SearchByMaterial(materials_df=df),
    ]

    if logger:
        # Replace only the final answer tool with the logged subclass
        #logged_tools = [LoggedTool(t, logger) for t in tools] ####
        logged_tools = []
        for t in tools:
            if isinstance(t, FinalAnswerTool):
                logged_tools.append(LoggedFinalAnswerTool(logger))
                #logged_tools.append(LoggedTool(t, logger))
            else:
                logged_tools.append(LoggedTool(t, logger))
        tools = logged_tools

    return CodeAgent(
            tools=tools,
            model=llm,
            instructions=instructions,
            add_base_tools=False,
            max_steps=10,
            additional_authorized_imports=[],
        )


if __name__ == "__main__":

    from matvisor.workshop.llm.llama import load_llama
    from matvisor.workshop.log import JSONLogger

    llm = load_llama(modelsize="7")

    # No logging
    #from matvisor.workshop.llm import _SmolAdapter
    #model = _SmolAdapter(llm)

    model = LoggingSmolAdapter(llm, logger=JSONLogger(path="agent_trace.jsonl"))
    prompt = """
    You are an expert materials specialist. Use tools that you have and don't invent or try to access any tools that you don't have.
    """
    agent = create_agent(model, system_prompt=prompt, logger=JSONLogger(path="agent_trace.jsonl"))
    out = agent.run("What is Terrazzoplatta?")
    print(out)