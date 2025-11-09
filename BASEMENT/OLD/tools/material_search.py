import pandas as pd
from smolagents import Tool
from fuzzywuzzy import process


class SearchByMaterial(Tool):
    """
    Create tool for searching materials database
    """

    name = "search_by_material"
    description = """
    Search a material database for a material to find its properties.
    """
    inputs = {
        "material": {
            "type": "string",
            "description": "The material to search for.",
            "nullable": True
        }
    }
    output_type = "any"

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__()

    def forward(self, material: str | None = None) -> str:
        if not material:
            return "Error: 'material' is required."
        try:
            # Read in materials database
            materials_df = pd.read_csv(self.file_path)

            # Get list of materials available in database
            material_names = materials_df["material"].dropna().tolist()

            # Find properties in database using fuzzy matching
            top_matches = process.extract(material, material_names, limit=5)
            threshold = 70
            filtered_matches = [match for match, score in top_matches if score >= threshold]

            if not filtered_matches:
                return f"Error: No close matches found for material '{material}'."

            # Get all matching materials
            matching_rows = materials_df[materials_df["material"].isin(filtered_matches)]

            # Convert results to a list of dictionaries
            results = matching_rows.to_dict(orient='records')

            return str(results)

        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":

    import os
    from matvisor.database import example_dataframe as df

    sample_file = "example_database.csv"
    df.to_csv(sample_file, index=False)

    search_tool = SearchByMaterial()
    result = search_tool.forward(file_path=sample_file, material="Copper")
    print("Search result:", result)

    # Clean up test CSV file
    if os.path.exists(sample_file):
        os.remove(sample_file)