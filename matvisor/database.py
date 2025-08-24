import pandas as pd


# List of properties
properties = {}

## Name of material
name_property = {
    "material": "The name of the material to add.",
}
properties.update(name_property)

## Physical properties
physical_properties = {
    "density": "The density value for the material. Units: g/cm^3. Single float number.",
    "melting": "The melting temperature value for the material. Units: °C. Single float number.",
    "young_modulus": "The Young modulus value for the material. Units: SI. Single float number.",
}
properties.update(physical_properties)

## List of properties
properties_list = list(properties.keys())

## Header for DataFrame
header = list(properties.keys())

# Example materials
example_materials = [
    ["Copper", 8.90, 1083, 110],
    ["Aluminum", 2.65, 660, 68],
    ["Iron", 7.85, 1538, 210],
    ["Wood", 0.60, None, 10],
]

# Create DataFrame
example_dataframe = pd.DataFrame(
    data=example_materials,
    columns=header
)


if __name__ == "__main__":
    print(example_dataframe)
    example_dataframe.to_csv("data/example_database.csv", header=True, index=False)