import os
from matvisor.run import run_pipeline
from matvisor.agent import build_agent
from matvisor.models_llama import LlamaCppModel, load_llama

#from dotenv import load_dotenv
#load_dotenv()

#print("ENV:", os.getenv("LLAMA_CPU_ONLY"), os.getenv("LLAMA_CTX"), os.getenv("LLAMA_BATCH"))

design = "kitchen utensil grip"
criterion = "heat resistant"

# Real scenarios: always use the actual local LLM when running main.py
#os.environ.setdefault("FORCE_CUDA", "1")

llm = load_llama("3")  # loads Qwen2.5-0.5B-Instruct GGUF via llama_cpp
model = LlamaCppModel(llm)
here = os.path.dirname(os.path.abspath(__file__))
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