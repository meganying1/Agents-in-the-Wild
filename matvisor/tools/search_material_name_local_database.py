import json
from smolagents import Tool
from fuzzywuzzy import process


class SearchMaterialNameLocalDatabase(Tool):
    """
    Tool for searching materials database.
    """

    name = "search_material_name_local_database"
    description = """
    Search your local material database for a material name to find its properties.
    """
    inputs = {
        "material": {
            "type": "string",
            "description": "The material to search for.",
            "nullable": True
        }
    }
    output_type = "any"

    def __init__(self, local_database):
        super().__init__()
        self.local_database = local_database

    def forward(self, material: str | None = None) -> str:
        if not material:
            return "Error: 'material' is required."
        try:
            local_database = self.local_database
            material_name_column = "Material Name"
            material_names = local_database[material_name_column].dropna().tolist()

            # Find properties in database using fuzzy matching
            top_matches = process.extract(material, material_names, limit=5)
            threshold = 80
            filtered_matches = [match for match, score in top_matches if score >= threshold]

            if not filtered_matches:
                return f"Error: No close matches found for material '{material}'."

            # Get all matching materials
            matching_rows = local_database[local_database[material_name_column].isin(filtered_matches)]

            # Convert results to a list of dictionaries
            results = matching_rows.to_dict(orient='records')

            return json.dumps(results, indent=1)

        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":

    import os
    from matvisor.database import load_materials_from_file

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(path)
    path = os.path.join(path, "database")
    filename = "database_test.csv"
    filepath = os.path.join(path, filename)
    df = load_materials_from_file(filepath)
    search_tool = SearchMaterialNameLocalDatabase(local_database=df)
    result = search_tool.forward(material="Terrazzoplatta")
    print("Search result:", result)