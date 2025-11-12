import os

#from matvisor.system_prompt import SYSTEM_PROMPT
from matvisor import (
    load_llama,
    qwen3_models_list,
    create_agent,
    Logger,
    ResultRecorder,
)

path = os.path.dirname(os.path.abspath(__file__))
result_path = os.path.join(path, "results")
result_filepath = os.path.join(result_path, "result.csv")
result_recorder = ResultRecorder(filepath=result_filepath)

question = """
In a few sentences, tell me who you are.
"""

for modelsize in qwen3_models_list:
    log_path = os.path.join(
        result_path,
        f"log_{modelsize}B.jsonl"
    )
    agent = create_agent(
        llama_model=load_llama(modelsize=modelsize),
        #system_prompt=SYSTEM_PROMPT,
        logger=Logger(path=log_path),
    )
    result = agent.run(question)
    result_recorder.add(modelsize=modelsize, result=result)
