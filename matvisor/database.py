import pandas as pd


# List of properties
properties = [
    "Material",
    "Density",
    "Melting",
    "Young's Modulus",
]

# Example materials
example_materials = [
    ["Copper", 8.90, 1083, 110],
    ["Aluminum", 2.65, 660, 68],
    ["Iron", 7.85, 1538, 210],
    ["Wood", 0.60, None, 10],
]

#example_data = deepcopy(header)
example_data = []
for material in example_materials:
    example_data.extend(material)

# Create DataFrame
example_dataframe = pd.DataFrame(example_materials, columns=properties)


if __name__ == "__main__":
    print(example_dataframe)