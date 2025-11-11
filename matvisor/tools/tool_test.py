"""
Dummy tool for testing purposes.
"""

from smolagents import Tool


class AddNumbers(Tool):
    name = "add_numbers"
    description = "Adds two numbers."
    inputs = {
        "a": {"type": "number", "description": "First number"},
        "b": {"type": "number", "description": "Second number"},
    }
    output_type = "number"

    def forward(self, a: float, b: float) -> float:
        return a + b
    

if __name__ == "__main__":
    a = 2
    b = 3
    tool = AddNumbers()
    result = tool.forward(a=a, b=b)
    print(result)