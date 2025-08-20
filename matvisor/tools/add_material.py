import pandas as pd
import numpy as np
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
            "description": "The melting temperature value for the material (single number).",
            "nullable": True
        },
        "density": {
            "type": "string",
            "description": "The density value for the material (single number).",
            "nullable": True
        },
        "elastic_mod": {
            "type": "string",
            "description": "The elastic modulus value for the material (single number).",
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

            # Parse a single numeric value or None
            def parse_value(val):
                if val is None:
                    return None
                if isinstance(val, (int, float)):
                    return float(val)
                val_str = str(val).strip()
                if val_str == "" or val_str.lower() == "none":
                    return None
                try:
                    return float(val_str)
                except ValueError:
                    raise ValueError(f"Invalid numeric value: '{val}'. Expected a single number or None.")
            
            # Get current property column names
            available_cols = [col for col in materials_df.columns]

            melting_val = parse_value(melting_temp)
            density_val = parse_value(density)
            elastic_val = parse_value(elastic_mod)

            # Function to find best match for a base property name
            def match_property(base_name):
                result = process.extractOne(base_name, available_cols)
                return result[0] if result else None
            
            # Fuzzy match input properties to database columns
            melting_col = match_property("melting")
            density_col = match_property("density")
            elastic_col = match_property("young's modulus")
            if not all([melting_col, density_col, elastic_col]):
                raise ValueError(
                    f"Could not find matching columns in CSV. Available columns: {available_cols}"
                )
            
            # Initialize new row
            new_row = {
                "Material": material,
                melting_col: melting_val,
                density_col: density_val,
                elastic_col: elastic_val,
            }

            # Append the new row without triggering concat warnings by expanding index, then scalar-assign
            next_idx = len(materials_df)
            materials_df = materials_df.reindex(range(next_idx + 1))
            for col in materials_df.columns:
                materials_df.at[next_idx, col] = new_row.get(col, np.nan)

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
    Quick smoke test for AddMaterial. Calls AddMaterial to append a new material row.
    """
    import os
    import tempfile
    from matvisor.database import example_dataframe

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        example_dataframe.to_csv(tmp.name, index=False)
        csv_path = tmp.name

    tool = AddMaterial()
    try:
        # Add a new material with single values
        result = tool.forward(
            file_path=csv_path,
            material="Testium",
            melting_temp="150",
            density="10.0",
            elastic_mod="205"
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