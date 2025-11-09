from smolagents import Tool
from langchain_community.utilities.arxiv import ArxivAPIWrapper


class ArxivSearch(Tool):
    """
    Create tool for searching Arxiv
    """

    name = "arxiv_search"
    description = "Search Arxiv, a free online archive of preprint and postprint manuscripts."
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
        arxiv_api = ArxivAPIWrapper(top_k_results=5)
        answer = arxiv_api.run(query)
        return answer


if __name__ == "__main__":
    
    import argparse

    parser = argparse.ArgumentParser(description="Test ArxivSearch tool.")
    parser.add_argument("--query", type=str, default="quantum computing", help="Query string for arXiv search")
    args = parser.parse_args()

    tool = ArxivSearch()
    result = tool.forward(args.query)
    print(result)