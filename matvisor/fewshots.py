FEWSHOTS = """
FEWSHOT Examples:
"""

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

Thought: Now I know wood is lightweight and commonly used. Let's return the result.
<code>
final_answer('wood')
</code>
"""

example_2 = """
Task: "You are tasked with designing a cooking pan. It should have a high melting point. What material would you recommend for this application?"

Thought: I will search Wikipedia (or a summary) for cookware properties.
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
Observation: "Matching materials found include medium carbon steels and low alloy steels."

Thought: I'll check arXiv summaries for these materials in pans. First, I'll check medium carbon steels. Next round, I'll check low alloy steels.
<code>
print(arxiv_search(query='medium carbon steel use in cooking pans'))
</code>
Observation: "Medium carbon steels is used in pans for heat resistance, durability, and toughness."

Thought: I'll check arXiv summaries for these materials in pans. This time, I'll check low alloy steels.
<code>
print(arxiv_search(query='low alloy steels use in cooking pans'))
</code>
Observation: "Low alloy steels is used in pans for heat resistance, durability, and toughness."

Thought: They are both great candidates. Return one of them randomly.
<code>
final_answer('medium carbon steel')
</code>
"""

example_3 = """
Task: "You are tasked with designing a cooking pan. It should have a low weight for maximum protability. What material would you recommend for this product?"

Thought: I will search Wikipedia (or a summary) for cookware properties.
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

examples = [
    example_1,
    example_2,
    example_3,
#    example_4,
#    example_5,
#    example_6,
#    example_7,
#    example_8,
]


for e in examples:
    FEWSHOTS += e + "\n\n"