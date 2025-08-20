import pandas as pd
from smolagents import Tool
from fuzzywuzzy import process


class SearchByProperty(Tool):
    """
    Create tool for searching materials database
    Currently requires agent to pass in a properties dictionary, may need to be changed.
    """

    name = "search_by_property"
    description = """
    Search a material database based on specified property ranges to find materials matching the given criteria.
    """
    inputs = {
        "file_path": {
            "type": "string",
            "description": "The path of the materials database file to search.",
            "nullable": True
        },
        "properties": {
            "type": "any",
            "description": "The properties to search for, with min and max values. Each property should be a dictionary with 'min' and 'max' keys.",
            "nullable": True
        }
    }
    output_type = "any"

    def __init__(self):
        super().__init__()

    def forward(self, file_path: str | None = None, properties: dict | None = None) -> str:
        if not file_path:
            return "Error: 'file_path' is required."
        if not properties:
            return "Error: 'properties' is required."
        try:
            # Read in materials database
            materials_df = pd.read_csv(file_path)

            # Find available properties in database
            avail_properties = [col for col in materials_df.columns]

            # Initialize a list to store matching materials
            matching_materials = []

            # Loop through each material in the database
            for index, row in materials_df.iterrows():
                match = True

                # Check each property in the provided dictionary
                for property_name, limits in properties.items():

                    # Check if the property exists in the dataframe using fuzzy matching (threshold can be adjusted)
                    matched_prop, score = process.extractOne(property_name, avail_properties)
                    if score < 50:
                        return f"Error: Could not find property '{property_name}'."
                    
                    try:
                        # Assuming that given database has min and max values
                        min_col = f"{matched_prop} min"
                        max_col = f"{matched_prop} max"

                        if min_col not in row or max_col not in row:
                            continue
                            # return f"Error: Property columns for '{matched_prop}' not found."
                        
                        # Check if material is within property limits
                        if "min" in limits and row[max_col] < limits["min"]:
                            match = False
                            break
                        if "max" in limits and row[min_col] > limits["max"]:
                            match = False
                            break

                    except Exception as e:
                        return f"Error while checking property '{property}': {str(e)}"
                
                # If the material matches all criteria, add it to the results
                if match:
                    matching_materials.append(row["Material"])

            # Return the list of matching materials
            return str(matching_materials) if matching_materials else "No materials found matching the criteria."

        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":
    
    import os

    # Create a small sample DataFrame
    data = {
        "Material": ["MaterialA", "MaterialB", "MaterialC"],
        "Density min": [2.5, 3.0, 1.5],
        "Density max": [3.5, 4.0, 2.5],
        "Conductivity min": [100, 150, 80],
        "Conductivity max": [200, 250, 120]
    }
    df = pd.DataFrame(data)

    # Save to a temporary CSV file
    test_csv = "test_materials.csv"
    df.to_csv(test_csv, index=False)

    # Create SearchByProperty instance
    search_tool = SearchByProperty()

    # Define properties dict that should match at least one material
    properties = {
        "Density": {"min": 2.0, "max": 3.6},
        "Conductivity": {"min": 90, "max": 210}
    }

    # Call forward method and print result
    result = search_tool.forward(file_path=test_csv, properties=properties)
    print("Search result:", result)

    # Clean up test CSV file
    if os.path.exists(test_csv):
        os.remove(test_csv)