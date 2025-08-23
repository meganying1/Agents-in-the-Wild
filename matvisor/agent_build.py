# agent_build.py
from smolagents import CodeAgent
from matvisor.prompt import SEARCH_PROMPT
from matvisor.tools import (
    AddMaterial,
    ArxivSearch,
    SearchByMaterial,
    SearchByProperty,
    WikipediaSearch,
)


def build_agent(model, verbosity="debug"):
    tools = [
        WikipediaSearch(),
        ArxivSearch(),
        SearchByMaterial(),
        SearchByProperty(),
        AddMaterial()
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

    agent = build_agent(FakeModel(), verbosity="debug")
    out = agent.run("Say 'hello' then call final_answer('done').")
    print("[agent_build] Agent run ->", out)