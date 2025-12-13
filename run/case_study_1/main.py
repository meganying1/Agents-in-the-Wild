import os

from matvisor import (
    DEFAULT_SYSTEM_PROMPT,
    qwen3_models_list,
    load_llama,
    create_agent,
    Logger,
    ResultRecorder,
)

path = os.path.dirname(os.path.abspath(__file__))
result_path = os.path.join(path, "results")
result_filepath = os.path.join(result_path, "result.csv")
result_recorder = ResultRecorder(filepath=result_filepath)

question_file = os.path.join(path, "question.txt")
with open(question_file, "r", encoding="utf-8") as f:
    question = f.read().strip()

for modelsize in qwen3_models_list:
    log_path = os.path.join(
        result_path,
        f"log_{modelsize}B.jsonl"
    )
    agent = create_agent(
        llama_model=load_llama(modelsize=modelsize),
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        logger=Logger(path=log_path),
    )
    result = agent.run(question)
    result_recorder.add(modelsize=modelsize, result=result)
