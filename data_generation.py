# Force cuda usage
import os
os.environ['FORCE_CUDA'] = '1'

##########################################################################################

import llama_cpp
from transformers import ReactCodeAgent
import regex as re
import pandas as pd
from data_generation_helper import SEARCH_PROMPT, WikipediaSearch, ArxivSearch, SearchByMaterial, SearchByProperty, AddMaterial, compile_question, append_results

##########################################################################################
# Code adapted from: https://github.com/grndnl/llm_material_selection_jcise/blob/main/generation/generation.py

# materials = ['steel', 'aluminum', 'titanium', 'glass', 'wood', 'thermoplastic', 'thermoset', 'elastomer', 'composite']

# for modelsize in ['1.5', '3', '7', '14', '32', '72']:
#     # Create LLM object
#     llm = llama_cpp.Llama.from_pretrained(
#         repo_id=f'bartowski/Qwen2.5-{modelsize}B-Instruct-GGUF',
#         filename=f'Qwen2.5-{modelsize}B-Instruct-Q4_K_M.gguf',
#         n_ctx=4096,
#         gpu=True,
#         metal=True,
#         n_gpu_layers=-1
#     )

#     # Define a function to call the LLM and return output
#     def llm_engine(messages, max_tokens=1000, stop_sequences=['Task']) -> str:
#         response = llm.create_chat_completion(
#             messages=messages,
#             stop=stop_sequences,
#             max_tokens=max_tokens,
#             temperature=0.6
#         )
#         answer = response['choices'][0]['message']['content']
#         return answer
    
#     # Create agent equipped with search tools
#     websurfer_agent = ReactCodeAgent(
#     system_prompt=SEARCH_PROMPT,
#     tools=[WikipediaSearch(), ArxivSearch(), MaterialsSearch()],
#     llm_engine=llm_engine,
#     add_base_tools = False,
#     verbose = True,
#     max_iterations=10
#     )
    
#     for question_type in ['agentic', 'zero-shot', 'few-shot', 'parallel', 'chain-of-thought']:
#         results = pd.DataFrame(columns=['design', 'criteria', 'material', 'response'])
#         for design in ['kitchen utensil grip', 'safety helmet', 'underwater component', 'spacecraft component']:
#             for criterion in ['lightweight', 'heat resistant', 'corrosion resistant', 'high strength']:
#                 if question_type == 'parallel':
#                     material = ', '.join(materials)
#                     question = compile_question(design, criterion,  material, question_type)
#                     response = llm_engine([{'role': 'user', 'content': question}])
#                     results = append_results(results, design, criterion, material, response, question_type)
#                 else:
#                     for material in materials:
#                         if question_type == 'agentic':
#                             question = compile_question(design, criterion, material, question_type)
#                             response = websurfer_agent.run(question)
#                             if isinstance(response, str): response = int(re.findall(r'\d+', response)[0])
#                         elif question_type in ['zero-shot', 'few-shot']:
#                             question = compile_question(design, criterion, material, question_type)
#                             response = llm_engine([{'role': 'user', 'content': question}])
#                             response = re.findall(r'\d+', response)[0]
#                         elif question_type == 'parallel':
#                             question = compile_question(design, criterion, [', '.join(materials)], question_type)
#                             response = llm_engine([{'role': 'user', 'content': question}])
#                         elif question_type == 'chain-of-thought':
#                             count = 0
#                             question = compile_question(design, criterion, material, question_type, count=count, )
#                             reasoning = llm_engine([{'role': 'user', 'content': question}], max_tokens=200)
#                             count = 1
#                             question = compile_question(design, criterion, material, question_type, count=count, reasoning=reasoning)
#                             response = llm_engine([{'role': 'user', 'content': question}])
#                         results = append_results(results, design, criterion, material, response, question_type)
#         # results.to_csv(f'Results/Data/qwen_{modelsize}B_{question_type}.csv', index=False)

##########################################################################################

for modelsize in ['7']:
    # Create LLM object
    llm = llama_cpp.Llama.from_pretrained(
        repo_id=f'bartowski/Qwen2.5-{modelsize}B-Instruct-GGUF',
        filename=f'Qwen2.5-{modelsize}B-Instruct-Q4_K_M.gguf',
        n_ctx=4096,
        gpu=True,
        metal=True,
        n_gpu_layers=-1
    )

    # Define a function to call the LLM and return output
    def llm_engine(messages, max_tokens=1000, stop_sequences=['Task']) -> str:
        response = llm.create_chat_completion(
            messages=messages,
            stop=stop_sequences,
            max_tokens=max_tokens,
            temperature=0.6
        )
        answer = response['choices'][0]['message']['content']
        return answer
    
    # Create agent equipped with search tools
    websurfer_agent = ReactCodeAgent(
    system_prompt=SEARCH_PROMPT,
    tools=[WikipediaSearch(), ArxivSearch(), SearchByMaterial(), SearchByProperty(), AddMaterial()],
    llm_engine=llm_engine,
    add_base_tools = False,
    verbose = True,
    max_iterations=10
    )
    
    results = pd.DataFrame(columns=['design', 'criteria', 'material', 'response'])
    for design in ['kitchen utensil grip', 'safety helmet', 'underwater component', 'spacecraft component']:
        for criterion in ['lightweight', 'heat resistant', 'corrosion resistant', 'high strength']:
            question = compile_question(design, criterion)
            response = websurfer_agent.run(question)
            results = append_results(results, design, criterion, response)
    results.to_csv(f'Data/test.csv', index=False)
