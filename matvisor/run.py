def _extract_final_answer(text: str) -> str | None:
    """
    Extract the payload from final_answer('...') or final_answer("...").
    Returns None if no exact final_answer call is present.
    """
    import re
    if not isinstance(text, str):
        return None
    m = re.findall(r"final_answer\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", text, flags=re.IGNORECASE)
    return m[-1] if m else None
"""
data_generation.py — standalone runner compatible with updated modules.

Usage:
    # Fast smoke run (no model load):
    python run.py
"""

import os
import pandas as pd

# Use the agent factory and local model shims that already exist in the project
from matvisor.agent import build_agent

# Prompt helpers remain in matvisor.prompt
from matvisor.prompt import compile_question


def run_pipeline(
        agent,
        design: str,
        criterion: str,
        results_path: str
    ) -> str:
    """
    Run the full question loop and write results to a separate CSV, leaving the materials DB intact.
    """
    # Make results directory
    os.makedirs(os.path.dirname(results_path) or ".", exist_ok=True)
    if os.path.exists(results_path):
        results = pd.read_csv(results_path)
    else:
        results = pd.DataFrame(columns=["design", "criteria", "response"])
    question = compile_question(design, criterion)
    response = agent.run(question)
    results = append_results(results, design, criterion, response)
    results.to_csv(results_path, index=False)
    return results_path

def append_results(results, design, criterion, response):
    results.loc[len(results)] = {
        'design': design,
        'criteria': criterion,
        'response': response
    }
    return results


if __name__ == "__main__":

    from matvisor.models_llama import FakeModel
    
    # FAST smoke test: always use FakeModel here
    os.environ.setdefault("FORCE_CUDA", "1")
    print("[run] FAST mode -> using FakeModel (no GGUF load).")

    model = FakeModel()
    agent = build_agent(model, database_path="some_path", verbosity="debug")

    # Quick sanity check (ensures agent wiring works)
    sanity = agent.run("Say 'hello' then call final_answer('ok').")
    print("[run] sanity ->", sanity)

    # Tiny one-iteration pipeline to exercise output code paths
    os.makedirs("data", exist_ok=True)
    results_path = "data/test_fast.csv"
    if os.path.exists(results_path):
        results = pd.read_csv(results_path)
    else:
        results = pd.DataFrame(columns=["design", "criteria", "response"])
    q = compile_question("kitchen utensil grip", "lightweight")
    r = agent.run(q)
    results = append_results(results, "kitchen utensil grip", "lightweight", r)
    results.to_csv(results_path, index=False)