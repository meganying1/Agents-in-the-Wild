import pandas as pd
from smolagents import Tool
from fuzzywuzzy import process


class SearchByProperty(Tool):
    """
    Create tool for searching materials database
    Requires agent to pass in a properties dictionary.
    """

    name = "search_by_property"
    description = """
    Search the material database by comparing target material properties to database values and ranking material names by distance.
    """
    inputs = {
        "properties": {
            "type": "any",
            "description": """
            Dictionary of target properties to search for. Keys can only include the following:
                - density: The density value for the material. Units: g/cm^3. Single float number.
                - melting: The melting temperature value for the material. Units: °C. Single float number.
                - young_modulus: The Young modulus value for the material. Units: SI. Single float number.
            """,
            "nullable": False
        }
    }
    output_type = "any"

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__()

    def forward(self, properties: dict | None = None) -> str:
        if not properties:
            return "Error: 'properties' is required."
        try:
            # Read in materials database
            materials_df = pd.read_csv(self.file_path)

            # Find available properties in database, excluding the label column
            avail_properties = [col for col in materials_df.columns if col != "material"]

            def parse_value(val):
                if val is None:
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                s = str(val).strip()
                if s == "" or s.lower() == "none":
                    return None
                return float(s)

            # Pre-resolve requested properties to dataframe columns via fuzzy match
            prop_map = {}
            for requested, target in properties.items():
                match, score = process.extractOne(requested, avail_properties)
                if score < 50:
                    return f"Error: Could not find property '{requested}'."
                prop_map[requested] = match

            results = []
            for _, row in materials_df.iterrows():
                per_prop = {}
                total_distance = 0.0
                valid = True
                for requested, match_col in prop_map.items():
                    target_val = parse_value(properties[requested])
                    if target_val is None:
                        valid = False
                        break
                    db_val = row.get(match_col)
                    # Skip rows where the database value is missing
                    if pd.isna(db_val):
                        valid = False
                        break
                    try:
                        diff = abs(float(db_val) - float(target_val))
                    except Exception:
                        valid = False
                        break
                    per_prop[match_col] = diff
                    total_distance += diff
                if valid:
                    result_row = {"material": row.get("material", ""), **per_prop, "total_distance": total_distance}
                    results.append(result_row)

            # Sort by total_distance ascending
            results.sort(key=lambda x: x["total_distance"])
            return str(results) if results else "No materials found matching the criteria."

        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":
    
    import os
    from matvisor.database import example_dataframe as df

    # Save to a temporary CSV file
    sample_file = "example_database.csv"
    df.to_csv(sample_file, index=False)

    # Create SearchByProperty instance
    search_tool = SearchByProperty()

    # Define properties dict that should match at least one material
    properties = {
        "density": 2.7,
    }

    # Call forward method and print result
    result = search_tool.forward(file_path=sample_file, properties=properties)
    print("Search result:", result)

    # Clean up test CSV file
    if os.path.exists(sample_file):
        os.remove(sample_file)