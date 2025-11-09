import json
from smolagents import Tool
from fuzzywuzzy import process


class SearchByMaterial(Tool):
    """
    Tool for searching materials database.
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

    def __init__(self, materials_df):
        super().__init__()
        self.materials_df = materials_df

    def forward(self, material: str | None = None) -> str:
        if not material:
            return "Error: 'material' is required."
        try:
            materials_df = self.materials_df
            material_name_column = "Material Name"
            material_names = materials_df[material_name_column].dropna().tolist()

            # Find properties in database using fuzzy matching
            top_matches = process.extract(material, material_names, limit=5)
            threshold = 70
            filtered_matches = [match for match, score in top_matches if score >= threshold]

            if not filtered_matches:
                return f"Error: No close matches found for material '{material}'."

            # Get all matching materials
            matching_rows = materials_df[materials_df[material_name_column].isin(filtered_matches)]

            # Convert results to a list of dictionaries
            results = matching_rows.to_dict(orient='records')

            return json.dumps(results, indent=2)

        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":

    import os
    from matvisor.database import load_materials_from_file

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(path)
    path = os.path.join(path, "database")
    filename = "AEC Material Database - Sheet1.csv"
    filepath = os.path.join(path, filename)
    df = load_materials_from_file(filepath)
    search_tool = SearchByMaterial(materials_df=df)
    result = search_tool.forward(material="Terrazzoplatta")
    print("Search result:", result)