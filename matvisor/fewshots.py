FEWSHOTS = """
FEWSHOT Examples:
"""

# 1. Search Wikipedia for relevant materials
# 2. Search database for material name
# 3. Return material name
example_1 = """
Task: "You are tasked with designing a cutting board. It should be lightweight. What material would you recommend for this application?"

Thought: I will search Wikipedia to find common materials used in cutting boards.
<code>
observation = wikipedia_search(query='common materials used in cutting boards')
print(observation)
</code>
Observation: "A material commonly used in cutting boards is wood."

Thought: Now I will search the materials database to find properties of wood.
<code>
observation = search_by_material(material="wood")
print(observation)
</code>
Observation: "{'Material': 'Wood', 'Density min': 0.3, 'Density max': 1.3, 'Thermal conductivity min': 0.1, 'Thermal conductivity max': 0.2}"

Thought: Now I know wood is lightweight and commonly used. Let's return it as the result.
<code>
final_answer('wood')
</code>
"""

# 1. Search Wikipedia for relevant materials
# 2. Search database using material properties
# 3. Search material name in arXiv for validation
# 4. Return material name
example_2 = """
Task: "You are tasked with designing a cooking pan. It should have a high melting point. What material would you recommend for this application?"

Thought: I will search Wikipedia to know cookware properties.
<code>
observation = wikipedia_search(query='necessary properties of cooking pans')
print(observation)
</code>
Observation: "High performance cookware uses materials with high thermal diffusivity and low reactivity."

Thought: I will search the database for high melting temperature along with good thermal conductivity and strength.
<code>
# (In your real tool you'd filter by properties; here we just mock the result)
print("Matching materials found include medium carbon steels and low alloy steels.")
</code>
Observation: "Matching materials found include steels."

Thought: I'll check arXiv summaries for steels in pans to validate my answer.
<code>
print(arxiv_search(query='Steel use in cooking pans'))
</code>
Observation: "Steel is used in pans for heat resistance, durability, and toughness."

Thought: I found the answer to return.
<code>
final_answer('steel')
</code>
"""

# 1. Search Wikipedia for relevant materials and found two candidate materials. Randomly choose one.
# 2. Search database for material name, not found.
# 3. Search Wikipedia for material properties.
# 4. Add material to database.
# 5. Return material name.
example_3 = """
Task: "You are tasked with designing a cooking pan. It should have a low weight for maximum protability. What material would you recommend for this product?"

Thought: I will search Wikipedia for light-weight cookware properties.
<code>
observation = wikipedia_search(query='necessary properties of portable low-weight cooking pans')
print(observation)
</code>
Observation: "Camping cookware is often made from lightweight materials like aluminum or titanium."

Thought: Now I will search the materials database to find properties of aluminium and I'll ignore titanium.
<code>
observation = search_by_material(material="aluminum")
print(observation)
</code>
Observation: "Material not found. So, I need to find it on wikipedia and add it to the database."

Thought: Now I will search wikipedia to find properties of aluminium..
<code>
observation = wikipedia_search(query='aluminium properties')
print(observation)
</code>
Observation: "Material: Aluminium, Density: 2.7, Thermal conductivity: 205, Yield strength: 55"

Thought: Now I will add aluminium to the database.
<code>
observation = add_material(material='aluminium', properties={"Density": 2.7, "Thermal conductivity": 205, "Yield strength": 55})
print(observation)
</code>
Observation: "Material aluminium added to the database."

Thought: I'll return aluminium as the final asnwer.
<code>
final_answer('aluminium')
</code>
"""

# 1. Search Wikipedia for relevant materials
# 2. Search database for material name
# 3. Return material name
example_4 = """
Task: "You are tasked with designing a cutting board. It should be lightweight. What material would you recommend for this application?"

Thought: I will search Wikipedia to find common materials used in cutting boards.
<code>
observation = wikipedia_search(query='common materials used in cutting boards')
print(observation)
</code>
Observation: "A material commonly used in cutting boards is wood."

Thought: Now I will search the materials database to find properties of wood.
<code>
observation = search_by_material(material="wood")
print(observation)
</code>
Observation: "Error: No close matches found for material 'wood'."

Thought: Wood doesn't exist on database. I need to find the wood properties on wikipedia and add it to the database.
<code>
observation = wikipedia_search(query='wood')
print(observation)
</code>
Observation: "{'material': 'wood', 'density': 0.3, 'melting': None}"

Thought: Adding wood to the database.
<code>
observation = add_material(material='wood', properties={'material': 'wood', 'density': 0.3, 'melting': None})
print(observation)
</code>
Observation: "Wood added to the database."

Thought: I'll return wood as the final asnwer. It seems like a good choice with good properties.
<code>
final_answer('wood')
</code>
"""

examples = [
    example_1,
    example_2,
    example_3,
    example_4,
#    example_5,
#    example_6,
#    example_7,
#    example_8,
]


for e in examples:
    FEWSHOTS += e + "\n\n"