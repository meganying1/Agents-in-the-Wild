
import os
from smolagents import Model

import llama_cpp
from smolagents import Tool, CodeAgent, FinalAnswerTool
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


SEARCH_PROMPT = ""


class WikipediaSearch(Tool):
    """
    Create tool for searching Wikipedia
    """

    name = "wikipedia_search"
    description = "Search Wikipedia, the free encyclopedia."
    inputs = {
        "query": {
            "type": "string",
            "description": "The search terms",
            "nullable": True
        },
    }
    output_type = "string"

    def __init__(self):
        super().__init__()

    def forward(self, query: str | None = None) -> str:
        if not query:
            return "Error: 'query' is required."
        wikipedia_api = WikipediaAPIWrapper(top_k_results=5)
        answer = wikipedia_api.run(query)
        return answer
    

def build_agent(model, verbosity="debug"):
    tools = [
        FinalAnswerTool(),
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
    
