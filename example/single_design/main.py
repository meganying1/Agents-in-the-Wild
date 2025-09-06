import os
from matvisor.run import run_pipeline
from matvisor.agent_build import build_agent
from matvisor.models_llama import LlamaCppModel, load_llama


design = "kitchen utensil grip"
criterion = "heat resistant"

# Real scenarios: always use the actual local LLM when running main.py
os.environ.setdefault("FORCE_CUDA", "1")

llm = load_llama("1.5")  # loads Qwen2.5-0.5B-Instruct GGUF via llama_cpp
model = LlamaCppModel(llm)
agent = build_agent(model, verbosity="info")
here = os.path.dirname(os.path.abspath(__file__))
run_pipeline(
    agent,
    design=design,
    criterion=criterion,
    db_csv=os.path.join(here, "database.csv"),
    results_csv=os.path.join(here, "result.csv")
)