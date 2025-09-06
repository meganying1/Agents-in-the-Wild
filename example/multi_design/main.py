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
        llm = load_llama("0.5")  # loads Qwen2.5-0.5B-Instruct GGUF via llama_cpp
        model = LlamaCppModel(llm)
        agent = build_agent(model, verbosity="info")
        out_path = run_pipeline(
            agent,
            design=design,
            criterion=criterion,
            db_csv=os.path.join(here, "data/example_database.csv"),
            results_csv=os.path.join(here, "result/design_results.csv")
        )
        print(f"[main] wrote {out_path}")