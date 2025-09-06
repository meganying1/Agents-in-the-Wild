# agent_build.py
from smolagents import CodeAgent, FinalAnswerTool
from matvisor.tools import (
    AddMaterial,
    ArxivSearch,
    SearchByMaterial,
    SearchByProperty,
    WikipediaSearch,
)
from matvisor.prompt import SEARCH_PROMPT


def build_agent(model, database_path: str, verbosity="debug"):
    tools = [
        FinalAnswerTool(),
        AddMaterial(file_path=database_path),
        ArxivSearch(),
        SearchByMaterial(file_path=database_path),
        SearchByProperty(file_path=database_path),
        WikipediaSearch(),
    ]
    max_steps = 10

    # Try newer enum-based API first; fall back to string-based API.
    try:
        from smolagents.agents import LogLevel  # may not exist or may miss some members
        level = {
            "quiet": getattr(LogLevel, "QUIET", getattr(LogLevel, "WARNING", None)),
            "info":  getattr(LogLevel, "INFO",  None),
            "debug": getattr(LogLevel, "DEBUG", None),
        }[verbosity]
        if level is None:
            raise AttributeError("Requested LogLevel not available in this version")
        return CodeAgent(
            tools=tools,
            model=model,
            instructions=SEARCH_PROMPT,
            add_base_tools=False,
            max_steps=max_steps,
            additional_authorized_imports=["pandas", "numpy", "fuzzywuzzy", "fuzzywuzzy.process"],
            verbosity_level=level,
        )
    except Exception:
        # Older builds: use plain string verbosity
        return CodeAgent(
            tools=tools,
            model=model,
            instructions=SEARCH_PROMPT,
            add_base_tools=False,
            max_steps=max_steps,
            additional_authorized_imports=["pandas", "numpy", "fuzzywuzzy", "fuzzywuzzy.process"],
            verbosity=verbosity,  # "debug" | "info" | "quiet"
        )


if __name__ == "__main__":

    from models_llama import FakeModel

    agent = build_agent(FakeModel(), database_path="somewhere", verbosity="debug")

    # show tool "names" regardless of whether agent.tools are instances or strings
    tools_field = getattr(agent, "tools", [])
    tool_names = []
    for t in tools_field:
        if isinstance(t, str):
            tool_names.append(t)
        elif hasattr(t, "name"):
            tool_names.append(t.name)
        else:
            tool_names.append(type(t).__name__)
    print("TOOLS:", tool_names)

    # show python-executor callables (what the executor will allow to run)
    af = getattr(agent.python_executor, "additional_functions", None)
    print("ADDITIONAL_FUNCTIONS:", sorted(af.keys()) if isinstance(af, dict) else af)

    out = agent.run("Say 'hello' then call final_answer('done').")
    print("[agent_build] Agent run ->", out)