"""
data_generation.py — standalone runner compatible with updated modules.

Usage:
    # Fast smoke run (no model load):
    python run.py

    # Heavy local model via llama.cpp (requires GGUF & llama_cpp):
    RUN_LLAMA=1 python run.py
"""
"""
Vision: agent(task: str, initial_library: pandas.DataFrame) -> str
"""

import os
import pandas as pd

# Use the agent factory and local model shims that already exist in the project
from matvisor.agent_build import build_agent
from matvisor.models_llama import FakeModel, LlamaCppModel, load_llama

# Prompt helpers remain in matvisor.prompt
from matvisor.prompt import compile_question, append_results


def run_pipeline(agent, out_csv: str = "data/test.csv") -> str:
    """
    Run the full question loop and write a CSV.
    """
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    results = pd.DataFrame(columns=["design", "criteria", "response"])

    for design in [
        "kitchen utensil grip",
        "safety helmet",
        "underwater component",
        "spacecraft component",
    ]:
        for criterion in [
            "lightweight",
            "heat resistant",
            "corrosion resistant",
            "high strength",
        ]:
            question = compile_question(design, criterion)
            response = agent.run(question)
            results = append_results(results, design, criterion, response)

    results.to_csv(out_csv, index=False)
    return out_csv


if __name__ == "__main__":
    # Allow GPU acceleration where applicable (safe no-op if unused)
    os.environ.setdefault("FORCE_CUDA", "1")

    use_llama = os.environ.get("RUN_LLAMA", "0") == "1"

    if use_llama:
        print("[data_generation] RUN_LLAMA=1 -> using local llama.cpp model.")
        llm = load_llama("7")  # loads Qwen2.5-7B-Instruct GGUF via llama_cpp
        model = LlamaCppModel(llm)
        agent = build_agent(model, verbosity="info")
        out_path = run_pipeline(agent, out_csv="data/test.csv")
        print(f"[data_generation] wrote {out_path}")
    else:
        print("[data_generation] FAST mode -> using FakeModel (no GGUF load).")
        model = FakeModel()
        agent = build_agent(model, verbosity="debug")

        # Quick sanity check (ensures agent wiring works)
        sanity = agent.run("Say 'hello' then call final_answer('ok').")
        print("[data_generation] sanity ->", sanity)

        # Tiny one-iteration pipeline to exercise output code paths
        os.makedirs("data", exist_ok=True)
        results = pd.DataFrame(columns=["design", "criteria", "response"])
        q = compile_question("kitchen utensil grip", "lightweight")
        r = agent.run(q)
        results = append_results(results, "kitchen utensil grip", "lightweight", r)
        results.to_csv("Data/test_fast.csv", index=False)
        print("[data_generation] wrote data/test_fast.csv")