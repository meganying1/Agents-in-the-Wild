from smolagents import Tool
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


class SearchWikipedia(Tool):
    """
    Create tool for searching Wikipedia
    """

    name = "search_wikipedia"
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
        wikipedia_api = WikipediaAPIWrapper(
            top_k_results=5,
            doc_content_chars_max=10000,
        )
        answer = wikipedia_api.run(query)
        return answer


if __name__ == "__main__":
    result = SearchWikipedia().forward("quantum computing")
    print(result)