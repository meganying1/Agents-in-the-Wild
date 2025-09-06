import pandas as pd
import numpy as np
from smolagents import Tool
from fuzzywuzzy import process

from matvisor.database import (
    name_property,
    physical_properties,
    properties_list
)


class AddMaterial(Tool):
    """
    Add material to the database.
    """

    name = "add_material"
    description = """
    Add a material and its properties to the material database.
    """

    inputs = {
        "material": {
            "type": "string",
            "description": "The name of the material to add.",
            "nullable": False
        },
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
    output_type = "string"

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__()

    def forward(
            self,
            material: str | None = None,
            properties: dict | None = None
        ):
        """
        Append one material row using explicit optional arguments.
        Any property not provided will be left as NaN in the CSV.
        """
        if not material:
            return "Error: 'material' is required."
        try:
            # Load DB
            df = pd.read_csv(self.file_path)

            # Helpers
            def parse_value(val):
                if val is None:
                    return np.nan
                if isinstance(val, (int, float)):
                    return float(val)
                s = str(val).strip()
                if s == "" or s.lower() == "none" or s.lower() == "nan":
                    return np.nan
                try:
                    return float(s)
                except ValueError:
                    # keep as text if it cannot be parsed to float
                    return s

            def match_property(base_name: str):
                # fuzzy match against known DB columns
                res = process.extractOne(base_name, properties_list)
                return res[0] if res else None

            # Build a full row with all columns set to NaN initially
            full_row = {col: np.nan for col in df.columns}

            # Set material name into the DB's name column (first key of name_property)
            name_col = list(name_property.keys())[0]
            full_row[name_col] = material

            # Map explicit args -> DB columns via fuzzy matching
            provided = properties
            for base_key, raw_val in provided.items():
                if raw_val is None:
                    continue
                col = match_property(base_key)
                if col is None:
                    continue
                full_row[col] = parse_value(raw_val)

            # Append row
            df = pd.concat([df, pd.DataFrame([full_row])], ignore_index=True)
            df.to_csv(self.file_path, index=False)
            return f"Material '{material}' added successfully."

        except Exception as e:
            return f"Error while adding material: {str(e)}"
        

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
            melting="150",
            young_modulus="200",
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