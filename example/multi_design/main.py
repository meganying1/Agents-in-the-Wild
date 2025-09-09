import os
from matvisor.run import run_pipeline
from matvisor.agent import build_agent
from matvisor.models_llama import LlamaCppModel, load_llama


# Real scenarios: always use the actual local LLM when running main.py
os.environ.setdefault("FORCE_CUDA", "1")
here = os.path.dirname(os.path.abspath(__file__))
designs = [
    "kitchen utensil grip",
    "safety helmet",
    "underwater component",
    "spacecraft component",
]
criterions = [
    "lightweight",
    "heat resistant",
    "corrosion resistant",
    "high strength",
]
for design in designs:
    for criterion in criterions:
        print("[main] Using local llama.cpp model for real scenarios.")
        llm = load_llama("3")   # loads Qwen2.5-<NUMBER>B-Instruct GGUF via llama_cpp
        model = LlamaCppModel(llm)
        agent = build_agent(
            model,
            database_path=os.path.join(here, "database.csv"),
            verbosity="info"
        )
        run_pipeline(
            agent,
            design=design,
            criterion=criterion,
            results_path=os.path.join(here, "result.csv")
        )