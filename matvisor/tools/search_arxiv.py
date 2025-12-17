from smolagents import Tool
import warnings
from langchain_community.utilities.arxiv import ArxivAPIWrapper


class SearchArxiv(Tool):
    """
    Create tool for searching Arxiv
    """

    name = "search_arxiv"
    description = "Search Arxiv, a free online archive of preprint and postprint manuscripts."
    inputs = {
        "query": {
            "type": "string",
            "description": "The search terms.",
            "nullable": True
        },
    }
    output_type = "string"

    def __init__(self):
        super().__init__()

    def forward(self, query: str | None = None) -> str:
        if not query:
            return "Error: 'query' is required."
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                module="langchain_community.utilities.arxiv"
            )

            arxiv_api = ArxivAPIWrapper(
                top_k_results=5,
                doc_content_chars_max=4000,
            )
            return arxiv_api.run(query)


if __name__ == "__main__":
    result = SearchArxiv().forward("quantum computing")
    print(result)