from smolagents import Tool
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


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


if __name__ == "__main__":
    """
    Quick smoke test for the WikipediaSearch tool.

    Usage:
        python -m matvisor.tools.wikipedia --query "cutting board materials"
    or:
        python /Users/aslan/Projects/Agents-in-the-Wild/matvisor/tools/wikipedia.py --query "cutting board materials"
    """
    
    import argparse
    import textwrap

    parser = argparse.ArgumentParser(
        description="Smoke test for matvisor.tools.wikipedia.WikipediaSearch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              python -m matvisor.tools.wikipedia --query "sustainable building materials"
              python matvisor/tools/wikipedia.py --query "carbon fiber"
            """
        ),
    )
    parser.add_argument(
        "--query",
        type=str,
        default="common materials used in cutting boards",
        help="Wikipedia search query (default: %(default)s)",
    )
    args = parser.parse_args()

    tool = WikipediaSearch()
    try:
        out = tool.forward(query=args.query)
        # Print a short preview to keep output tidy.
        preview = (out[:500] + " ...") if isinstance(out, str) and len(out) > 500 else out
        print("[WikipediaSearch] OK")
        print(preview)
    except Exception as e:
        print("[WikipediaSearch] FAIL:", e)
        raise