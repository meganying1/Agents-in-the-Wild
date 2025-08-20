import pandas as pd
from smolagents import Tool
from fuzzywuzzy import process


class AddMaterial(Tool):
    """
    Add material to the database.
    """

    name = "add_material"
    description = """
    Add a material and its properties to the material database.
    """

    inputs = {
        "file_path": {
            "type": "string",
            "description": "The path of the materials database file to update.",
            "nullable": True
        },
        "material": {
            "type": "string",
            "description": "The name of the material to add.",
            "nullable": True
        },
        "melting_temp": {
            "type": "string",
            "description": "The range of melting temperature for the material to add in min-max format.",
            "nullable": True
        },
        "density": {
            "type": "string",
            "description": "The range of density for the material to add in min-max format.",
            "nullable": True
        },
        "elastic_mod": {
            "type": "string",
            "description": "The range of elastic modulus for the material to add in min-max format.",
            "nullable": True
        }
    }
    output_type = "any"

    def __init__(self):
        super().__init__()

    def forward(self, file_path: str | None = None, material: str | None = None, melting_temp=None, density=None, elastic_mod=None):
        if not file_path:
            return "Error: 'file_path' is required."
        if not material:
            return "Error: 'material' is required."
        try: 
            # Read in materials database
            materials_df = pd.read_csv(file_path)

            # Parse the range strings into min and max values
            def parse_range(rng):
                if not rng: return None, None
                parts = rng.replace(" ", "").split("-")
                if len(parts) != 2:
                    raise ValueError(f"Invalid range format: '{rng}'. Expected format 'min-max'.")
                return float(parts[0]), float(parts[1])
            
            # Get current property column names
            available_cols = [col for col in materials_df.columns]

            melting_min, melting_max = parse_range(melting_temp)
            density_min, density_max = parse_range(density)
            elastic_min, elastic_max = parse_range(elastic_mod)

            # Function to find best match for a base property name
            def match_property(base_name):
                min_match, _ = process.extractOne(base_name + " min", available_cols)
                max_match, _ = process.extractOne(base_name + " max", available_cols)
                return min_match, max_match
            
            # Fuzzy match input properties to database columns
            melting_min_col, melting_max_col = match_property("melting")
            density_min_col, density_max_col = match_property("density")
            elastic_min_col, elastic_max_col = match_property("young's modulus")
            
            # Initialize new row
            new_row = {
                "Material": material,
                melting_min_col: melting_min,
                melting_max_col: melting_max,
                density_min_col: density_min,
                density_max_col: density_max,
                elastic_min_col: elastic_min,
                elastic_max_col: elastic_max
            }

            # Append the new row to the database
            materials_df = pd.concat([materials_df, pd.DataFrame([new_row])], ignore_index=True)

            # Save the updated database to file path
            materials_df.to_csv(file_path, index=False)
            return f"Material '{material}' added/updated successfully."

        except Exception as e:
            return f"Error while adding material: {str(e)}"
        
            # # Track missing properties
            # missing = []

            # # Loop through all required properties
            # for prop in self.required_properties:
            #     if prop in properties and isinstance(properties[prop], dict):
            #         min_val = properties[prop].get("min", "")
            #         max_val = properties[prop].get("max", "")
            #     else:
            #         min_val = ""
            #         max_val = ""
            #         missing.append(prop)

            #     new_row[f"{prop} min"] = min_val
            #     new_row[f"{prop} max"] = max_val

            # try:
            #     # Append new row to the DataFrame
            #     self.materials_df = self.materials_df.append(new_row, ignore_index=True)
            #     self.materials_df.to_csv('/Users/mying/Documents/Design Research Collective/Material Selection/Data/material_properties_minmax.csv', index=False)

            #     if missing:
            #         return (
            #             f"Material '{material}' was added to the database with the available properties.\n\n"
            #             f"However, some properties are missing:\n- " + "\n- ".join(missing) + "\n\n"
            #             f"To find these, you can use:\n"
            #             f"```python\nwikipedia_search(query=\"{material} {missing[0]} properties\")\n```\n"
            #             f"Then update the material entry by re-running `add_material` with the missing data."
            #         )
            #     else:
            #         return f"Material '{material}' successfully added with all properties."

            # except Exception as e:
            #     return f"Error while adding material: {str(e)}"
            

if __name__ == "__main__":
    """
    Quick smoke test for AddMaterial.

    Creates a tiny CSV with columns:
      - Material
      - melting min/max
      - density min/max
      - young's modulus min/max
    Then calls AddMaterial to append a new material row.
    """
    import os
    import tempfile

    # Build a tiny starter CSV
    df = pd.DataFrame([
        {
            "Material": "Aluminum",
            "melting min": 600.0, "melting max": 700.0,
            "density min": 2.6,   "density max": 2.8,
            "young's modulus min": 68.0, "young's modulus max": 72.0
        }
    ])
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        csv_path = tmp.name

    tool = AddMaterial()
    try:
        # Add a new material with simple ranges
        result = tool.forward(
            file_path=csv_path,
            material="Testium",
            melting_temp="100-200",
            density="9.5-10.5",
            elastic_mod="200-210"
        )
        print("[AddMaterial] forward ->", result)

        # Show the updated CSV content
        updated = pd.read_csv(csv_path)
        print("[AddMaterial] Updated rows:")
        print(updated.to_string(index=False))
    finally:
        # Clean up temp file
        try:
            os.remove(csv_path)
        except OSError:
            pass