"""
data_generation.py — standalone runner compatible with updated modules.

Usage:
    # Fast smoke run (no model load):
    python run.py
"""

import os
import pandas as pd

# Use the agent factory and local model shims that already exist in the project
from matvisor.agent_build import build_agent
from matvisor.models_llama import FakeModel

# Prompt helpers remain in matvisor.prompt
from matvisor.prompt import compile_question, append_results


def run_pipeline(
        agent,
        db_csv="data/example_database.csv",
        results_csv="result/design_results.csv"
    ) -> str:
    """
    Run the full question loop and write results to a separate CSV, leaving the materials DB intact.
    """
    os.makedirs(os.path.dirname(results_csv) or ".", exist_ok=True)
    results = pd.DataFrame(columns=["design", "criteria", "response"])
    
    # Read DB schema once and pass it to the model as a hard constraint
    db_cols = pd.read_csv(db_csv, nrows=0).columns.tolist()
    schema_hint = (
        "Materials DB columns: " + ", ".join(db_cols) + ". "
        "Only use these existing column names. Do NOT invent new columns. "
        #"If a needed property is missing, reason using available columns instead of querying it; "
        #"when updating the CSV, you may only read/write these columns. "
        #"Return the final answer ONLY by calling final_answer('<one material name>') — ideally one that exists in the DB (Material column) or that you first add via add_material; do not include extra narration in the final_answer."
    )


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
            question += (
                f"\n\n{schema_hint}\n"
                f'When you need to read or update the database, call tools with file_path="{db_csv}".\n'
                f'Save the results to {results_csv}.\n'
            )
            response = agent.run(question)
            results = append_results(results, design, criterion, response)

    results.to_csv(results_csv, index=False)
    return results_csv


if __name__ == "__main__":
    # FAST smoke test: always use FakeModel here
    os.environ.setdefault("FORCE_CUDA", "1")
    print("[run] FAST mode -> using FakeModel (no GGUF load).")

    model = FakeModel()
    agent = build_agent(model, verbosity="debug")

    # Quick sanity check (ensures agent wiring works)
    sanity = agent.run("Say 'hello' then call final_answer('ok').")
    print("[run] sanity ->", sanity)

    # Tiny one-iteration pipeline to exercise output code paths
    os.makedirs("data", exist_ok=True)
    results = pd.DataFrame(columns=["design", "criteria", "response"])
    q = compile_question("kitchen utensil grip", "lightweight")
    q = (
        q
        + "\n\nMaterials database CSV path: data/example_database.csv\n"
        + 'When you need to read or update the database, call tools with file_path="data/example_database.csv".'
    )
    r = agent.run(q)
    results = append_results(results, "kitchen utensil grip", "lightweight", r)
    results.to_csv("data/test_fast.csv", index=False)