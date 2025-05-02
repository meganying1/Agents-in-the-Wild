import pandas as pd
from dotenv import load_dotenv
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from transformers import Tool
from fuzzywuzzy import process
load_dotenv()
    
##########################################################################################

import pandas as pd
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from transformers import Tool
    
##########################################################################################

# Create tool for searching Wikipedia
class WikipediaSearch(Tool):
    name = "wikipedia_search"
    description = "Search Wikipedia, the free encyclopedia."

    inputs = {
        "query": {
            "type": "string",
            "description": "The search terms",
        },
    }
    output_type = "string"

    def __init__(self):
        super().__init__()

    def forward(self, query: str) -> str:
        wikipedia_api = WikipediaAPIWrapper(top_k_results=5)
        answer = wikipedia_api.run(query)
        return answer

# Create tool for searching Arxiv
class ArxivSearch(Tool):
    name = "arxiv_search"
    description = "Search Arxiv, a free online archive of preprint and postprint manuscripts."

    inputs = {
        "query": {
            "type": "string",
            "description": "The search terms",
        },
    }
    output_type = "string"

    def __init__(self):
        super().__init__()

    def forward(self, query: str) -> str:
        arxiv_api = ArxivAPIWrapper(top_k_results=5)
        answer = arxiv_api.run(query)
        return answer

# Create tool for searching materials database
# Currently requires agent to pass in a properties dictionary, may need to be changed
class SearchByProperty(Tool):
    name = "search_by_property"
    description = """
    Search a material database based on specified property ranges to find materials matching the given criteria.
    """

    inputs = {
        "file_path": {
            "type": "string",
            "description": "The path of the materials database file to search."
        },
        "properties": {
            "type": "any",
            "description": "The properties to search for, with min and max values. Each property should be a dictionary with 'min' and 'max' keys."
        }
    }
    output_type = "any"

    def __init__(self):
        super().__init__()

    def forward(self, file_path: str, properties: dict) -> str:
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
        
# Create tool for searching materials database
class SearchByMaterial(Tool):
    name = "search_by_material"
    description = """
    Search a material database for a material to find its properties.
    """

    inputs = {
        "file_path": {
            "type": "string",
            "description": "The path of the materials database file to search."
        },
        "material": {
            "type": "string",
            "description": "The material to search for."
        }
    }
    output_type = "any"

    def __init__(self):
        super().__init__()

    def forward(self, file_path: str, material: str) -> str:
        try:
            # Read in materials database
            materials_df = pd.read_csv(file_path)

            # Get list of materials available in database
            material_names = materials_df["Material"].dropna().tolist()

            # Find properties in database using fuzzy matching
            top_matches = process.extract(material, material_names, limit=5)
            threshold = 70
            filtered_matches = [match for match, score in top_matches if score >= threshold]

            if not filtered_matches:
                return f"Error: No close matches found for material '{material}'."

            # Get all matching materials
            matching_rows = materials_df[materials_df["Material"].isin(filtered_matches)]

            # Convert results to a list of dictionaries
            results = matching_rows.to_dict(orient='records')

            return str(results)

        except Exception as e:
            return f"Error: {str(e)}"
        
# Create tool to add material and its properties to materials database
class AddMaterial(Tool):
    name = "add_material"
    description = """
    Add a material and its properties to the material database.
    """

    inputs = {
        "file_path": {
            "type": "string",
            "description": "The path of the materials database file to update."
        },
        "material": {
            "type": "string",
            "description": "The name of the material to add."
        },
        "melting_temp": {
            "type": "string",
            "description": "The range of melting temperature for the material to add in min-max format."
        },
        "density": {
            "type": "string",
            "description": "The range of density for the material to add in min-max format."
        },
        "elastic_mod": {
            "type": "string",
            "description": "The range of elastic modulus for the material to add in min-max format."
        }
    }
    output_type = "any"

    def __init__(self):
        super().__init__()

    def forward(self, file_path: str, material: str, melting_temp=None, density=None, elastic_mod=None):
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

##########################################################################################

# Custom system prompt
SEARCH_PROMPT = '''
You are an expert assistant who can solve any task using code blobs. You will be given a task to solve as best you can.
To do so, you have been given access to a list of tools: these tools are basically Python functions which you can call with code.
To solve the task, you must plan forward to proceed in a series of steps, in a cycle of 'Thought:', 'Code:', and 'Observation:' sequences.

At each step, in the 'Thought:' sequence, you should first explain your reasoning towards solving the task and the tools that you want to use.
Then in the 'Code:' sequence, you should write the code in simple Python. The code sequence must end with '<end_action>' sequence.
During each intermediate step, you can use 'print()' to save whatever important information you will then need.
These print outputs will then appear in the 'Observation:' field, which will be available as input for the next step.
In the end you have to return a final answer using the `final_answer` tool.

You are provided with the following tools:
<<tool_description>>

Here are some examples:
---
Task: "You are tasked with designing a cutting board. It should be lightweight. What material would you recommend for this application?"

Thought: I will search Wikipedia to find common materials used in cutting boards.
Code:
```py
observation = wikipedia_search(query = 'common materials used in cutting boards')
print(observation)
```<end_action>
Observation: "A material commonly used in cutting boards is wood."

Thought: Now I will search the materials database to find properties of wood.
Code:
```py
observation = search_by_material(material="wood")
print(observation)
```<end_action>
Observation: "{'Material': 'Wood', 'Material category': 'Natural materials', 'Melting/glass temperature min': None, 'Melting/glass temperature max': None, 'Density min': 0.3, 'Density max': 1.3, 'Young's modulus min': 5.0, 'Young's modulus max': 18.0, 'Yield strength min': 30.0, 'Yield strength max': 100.0, 'Tensile strength min': 40.0, 'Tensile strength max': 150.0, 'Fracture toughness (plane-strain) min': 2.0, 'Fracture toughness (plane-strain) max': 6.0, 'Thermal conductivity min': 0.1, 'Thermal conductivity max': 0.2, 'Thermal expansion min': 3.0, 'Thermal expansion max': 6.0, 'Production energy min': 0.5, 'Production energy max': 2.0, 'CO2 burden min': 0.01, 'CO2 burden max': 0.1, 'Flammability resistance': 'E', 'Fresh water resistance': 'C', 'Salt water resistance': 'D', 'Sunlight (UV) resistance': 'C', 'Wear resistance': 'C'}"

Thought: Now I know that wood is a lightweight material commonly used in cutting boards. Let's return the result.
Code:
```py
final_answer('woods')
```<end_action>
---
Task: "You are tasked with designing a cooking pan. It should have a high melting point. What material would you recommend for this application?"

Thought: I will search Wikipedia to find the necessary properties of cooking pans.
Code:
```py
observation = wikipedia_search(query = 'necessary properties of cooking pans')
print(observation)
```<end_action>
Observation: "High performance cookware is made from materials that combine high thermal diffusivity and low reactivity to produce a vessel that evenly distributes heat and does not react with the food being cooked."

Thought: Now I know what the necessary properties of cooking pans are. I will search the materials database to find materials that to find materials with a high melting/glass temperature along with good thermal conductivity and strength.
Code:
```py
observation = search_by_property(properties={
    "Melting/glass temperature": {"min": 1500.0},
    "Thermal conductivity": {"min": 30.0},
    "Yield strength": {"min": 500.0},
    "Fracture toughness (plane-strain)": {"min": 7.0}
})
print(observation)
```<end_action>
Observation: "Matching materials found include medium carbon steels and low alloy steels."

Thought: Now I will search Arxiv to see what research says about using medium carbon steel in cooking pans.
Code:
```py
observation = arxiv_search(query = 'medium carbon steel use in cooking pans')
print(observation)
```<end_action>
Observation: "Studies show medium carbon steels are often used in cooking pans due to their balance of strength, heat resistance, and durability. They provide a good combination of wear resistance and toughness, making them suitable for cookware applications, especially in high-heat environments."

Thought: Now I will search Arxiv to see what research says about using low alloy steel in cooking pans.
Code:
```py
observation = arxiv_search(query = 'low alloy steel use in cooking pans')
print(observation)
```<end_action>
Observation: "Low alloy steels are used in cooking pans for their combination of heat resistance, durability, and corrosion resistance. These steels are commonly chosen for cookware due to their ability to withstand high temperatures while maintaining strength and toughness."

Thought: Now I know medium carbon steels and low alloy steels meet the necessary criteria. Let's return the result.
Code:
```py
final_answer('medium carbon steel or low alloy steel')
```<end_action>
---

On top of performing computations in the Python code snippets that you create, you have access to these tools (and no other tool):
<<tool_descriptions>>

Here are the rules you should always follow to solve your task:
1. Always provide a 'Thought:' sequence, and a 'Code:\n```py' sequence ending with '```<end_action>' sequence, else you will fail.
2. Use only variables that you have defined!
3. Always use the right arguments for the tools. DO NOT pass the arguments as a dict as in 'answer = wiki({'query': "What is the place where James Bond lives?"})', but use the arguments directly as in 'answer = wiki(query="What is the place where James Bond lives?")'.
4. Take care to not chain too many sequential tool calls in the same code block, especially when the output format is unpredictable. For instance, a call to search has an unpredictable return format, so do not have another tool call that depends on its output in the same block: rather output results with print() to use them in the next block.
5. Call a tool only when needed, and never re-do a tool call that you previously did with the exact same parameters.
6. Don't name any new variable with the same name as a tool: for instance don't name a variable 'final_answer'.
7. Never create any notional variables in our code, as having these in your logs might derail you from the true variables.
8. You can use imports in your code, but only from the following list of modules: <<authorized_imports>>
9. The state persists between code executions: so if in one step you've created variables or imported modules, these will all persist.
10. Don't give up! You're in charge of solving the task, not providing directions to solve it.

If you solve the task correctly, you will receive a reward of $1,000,000. Now begin!
'''

##########################################################################################
# Code adapted from: https://github.com/grndnl/llm_material_selection_jcise/blob/main/generation/generation.py

def compile_question(design, criterion):
    question = f'You are a material science and design engineer expert.\n' \
                f'You are tasked with designing a {design}. The design should be {criterion}.\n' \
                f'What material would you recommend for this application?'
    return question

def append_results(results, design, criterion, response):
    results = results._append({
        'design': design,
        'criteria': criterion,
        'response': response
    }, ignore_index=True)
    return results
