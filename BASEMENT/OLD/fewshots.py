FEWSHOTS = """
FEWSHOT Examples:
"""

# 1. Search Wikipedia for relevant materials
# 2. Search database for material name
# 3. Return material name
example_1 = """
Task: "You are tasked with designing a cutting board. It should be lightweight. What material would you recommend for this application?"

Thought: I will search Wikipedia to find common materials used in cutting boards.
Code:
<code>
observation = wikipedia_search(query='common materials used in cutting boards')
print(observation)
</code>
<end_action>
Observation: Page: cutting board\nCutting board is a common utensil to cut materials and the materials commonly used in cutting boards are wood and plastic.

Thought: Based on the observation, I will search the materials database to find properties of wood.
Code:
<code>
observation = search_by_material(material="wood")
print(observation)
</code>
<end_action>
Observation: {'Material': 'Wood', 'Density min': 0.3, 'Density max': 1.3, 'Thermal conductivity min': 0.1, 'Thermal conductivity max': 0.2}"

Thought: Now I know wood is lightweight and commonly used. Let's return it as the result.
Code:
<code>
final_answer('wood')
</code>
<end_action>
"""

# 1. Search Wikipedia for relevant materials
# 2. Search database using material properties
# 3. Search material name in arXiv for validation
# 4. Return material name
example_2 = """
Task: "You are tasked with designing a cooking pan. It should have a high melting point. What material would you recommend for this application?"

Thought: I will search Wikipedia to know cookware properties.
Code:
<code>
observation = wikipedia_search(query='necessary properties of cooking pans')
print(observation)
</code>
<end_action>
Observation: High performance cookware uses materials with high thermal diffusivity and low reactivity.

Thought: I will search the database for high melting temperature along with good thermal conductivity and strength.
Code:
<code>
# (In your real tool you'd filter by properties; here we just mock the result)
print("Matching materials found include medium carbon steels and low alloy steels.")
</code>
<end_action>
Observation: Matching materials found include steels.

Thought: I'll check arXiv summaries for steels in pans to validate my answer.
Code:
<code>
observation = arxiv_search(query='Steel use in cooking pans')
print(observation)
</code>
<end_action>
Observation: Steel is used in pans for heat resistance, durability, and toughness.

Thought: I found the answer to return.
Code:
<code>
final_answer('steel')
</code>
<end_action>
"""

# 1. Search Wikipedia for relevant materials and found two candidate materials. Randomly choose one.
# 2. Search database for material name, not found.
# 3. Search Wikipedia for material properties.
# 4. Add material to database.
# 5. Return material name.
example_3 = """
Task: "You are tasked with designing a cooking pan. It should have a low weight for maximum protability. What material would you recommend for this product?"

Thought: I will search Wikipedia for light-weight cookware properties.
Code:
<code>
observation = wikipedia_search(query='necessary properties of portable low-weight cooking pans')
print(observation)
</code>
<end_action>
Observation: Camping cookware is often made from lightweight materials like aluminum or titanium.

Thought: Now I will search the materials database to find properties of aluminum and I'll ignore titanium.
Code:
<code>
observation = search_by_material(material="aluminum")
print(observation)
</code>
<end_action>
Observation: Material not found. So, I need to find it on wikipedia and add it to the database.

Thought: Now I will search wikipedia to find properties of aluminum.
Code:
<code>
observation = wikipedia_search(query='aluminum properties')
print(observation)
</code>
<end_action>
Observation: Material: aluminum, Density: 2.7, Thermal conductivity: 205, Yield strength: 55"

Thought: Now I will add aluminum to the database.
Code:
<code>
observation = add_material(material='aluminum', properties={"Density": 2.7, "Thermal conductivity": 205, "Yield strength": 55})
print(observation)
</code>
<end_action>
Observation: Material aluminum added to the database.

Thought: I'll return aluminum as the final asnwer.
Code:
<code>
final_answer('aluminum')
</code>
<end_action>
"""

# 1. Search Wikipedia for relevant materials
# 2. Search database for material name
# 3. Return material name
example_4 = """
Task: "You are tasked with designing a cutting board. It should be lightweight. What material would you recommend for this application?"

Thought: I will search Wikipedia to find common materials used in cutting boards.
Code:
<code>
observation = wikipedia_search(query='common materials used in cutting boards')
print(observation)
</code>
<end_action>
Observation: A material commonly used in cutting boards is wood.

Thought: Now I will search the materials database to find properties of wood.
Code:
<code>
observation = search_by_material(material="wood")
print(observation)
</code>
<end_action>
Observation: Error: No close matches found for material 'wood'.

Thought: Wood doesn't exist on database. I need to find the wood properties on wikipedia and add it to the database.
Code:
<code>
observation = wikipedia_search(query='wood')
print(observation)
</code>
<end_action>
Observation: {'material': 'wood', 'density': 0.3, 'melting': None}"

Thought: Adding wood to the database.
Code:
<code>
observation = add_material(material='wood', properties={'material': 'wood', 'density': 0.3, 'melting': None})
print(observation)
</code>
<end_action>
Observation: Wood added to the database.

Thought: I'll return wood as the final asnwer. It seems like a good choice with good properties.
Code:
<code>
final_answer('wood')
</code>
<end_action>
"""

# 1. Search Wikipedia for relevant materials (handles/grips for high heat)
# 2. Search database for material name; if missing, fetch props and add
# 3. Return material name
example_5 = """
Task: "You are tasked with designing a kitchen utensil grip. The design should be heat resistant. What material would you recommend for this application?"

Thought: I will search Wikipedia for heat-resistant handle materials commonly used on cookware and utensils.
Code:
<code>
observation = wikipedia_search(query='heat resistant handle materials cookware utensil grips')
print(observation)
</code>
<end_action>
Observation: Common heat-resistant grip materials include silicone rubber (usable ~200–250°C), phenolic resin (used in cookware handles), and wood (moderate heat resistance).

Thought: Silicone rubber is widely used for utensil grips and offers high thermal stability and good grip. I will search the database for silicone.
Code:
<code>
observation = search_by_material(material="silicone")
print(observation)
</code>
<end_action>
Observation: Material not found in database. I should fetch its properties and add it.

Thought: I will search Wikipedia for silicone rubber properties to get density and temperature limits.
Code:
<code>
observation = wikipedia_search(query='silicone rubber properties temperature limit density')
print(observation)
</code>
<end_action>
Observation: Material: Silicone rubber, Density: 1.1, Max service temperature: 200–250 °C, Notes: good thermal stability and grip, food-safe grades available.

Thought: Now I will add silicone to the database with the gathered properties.
Code:
<code>
observation = add_material(material='silicone', properties={'Density': 1.1, 'Max service temperature (C)': 230, 'Notes': 'Food-safe silicone rubber; good grip; heat resistant'})
print(observation)
</code>
<end_action>
Observation: Material silicone added to the database.

Thought: I will return silicone as the final answer.
Code:
<code>
final_answer('silicone')
</code>
<end_action>
"""

examples = [
    example_1,
    example_2,
    example_3,
    example_4,
    example_5,
]


for e in examples:
    FEWSHOTS += e + "\n\n"