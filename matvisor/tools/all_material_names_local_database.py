import json
from smolagents import Tool


class AllMaterialNamesLocalDatabase(Tool):
    """
    Tool for retrieving all material names from local database.
    """

    name = "all_material_names_local_database"
    description = """
    Retrieve all material names from local database.
    """
    inputs = {}
    output_type = "any"

    def __init__(self, local_database):
        super().__init__()
        self.local_database = local_database

    def forward(self) -> str:
        try:
            local_database = self.local_database
            material_name_column = "Material Name"
            material_names = local_database[material_name_column].dropna().tolist()
            return json.dumps(material_names, indent=1)

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
    search_tool = AllMaterialNamesLocalDatabase(local_database=df)
    result = search_tool.forward()
    print("Result:", result)