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
from matvisor.agent_build import build_agent
from matvisor.models_llama import FakeModel

# Prompt helpers remain in matvisor.prompt
from matvisor.prompt_old import compile_question, append_results


def run_pipeline(
        agent,
        design: str,
        criterion: str,
        db_csv="data/database.csv",
        results_csv="result/design_results.csv"
    ) -> str:
    """
    Run the full question loop and write results to a separate CSV, leaving the materials DB intact.
    """
    os.makedirs(os.path.dirname(results_csv) or ".", exist_ok=True)
    results = pd.DataFrame(columns=["design", "criteria", "response"])
    
    # Read DB schema once and pass it to the model as a hard constraint
    db_cols = pd.read_csv(db_csv, nrows=0).columns.tolist()
    db_cols = db_cols[2:]
    schema_hint = (
        "Materials DB columns represents material properties. The columns are: " + ", ".join(db_cols) + ". "
        "Only use these existing column names. Do NOT invent new columns. "
        "Return the final answer ONLY by calling final_answer('<one material name>'). "
        "Do not include any narration or extra text in the final_answer call. "
        "If you must add a new material first, then call add_material, and finally call final_answer('<that material name>'). "
    )
    question = compile_question(design, criterion)
    question += (
        f"\n\n{schema_hint}\n"
        f'When you need to read or update the database, call tools with file_path="{db_csv}".\n'
        f'Pick exactly one from the material names in the database or search and add to DB, then end with final_answer(<name>).\n'
        f'Save the results to {results_csv}.\n'
    )
    response = agent.run(question)
    # Prefer an exact final_answer('...') payload; otherwise fall back to raw response
    extracted = _extract_final_answer(response)
    payload = extracted if extracted is not None else response
    results = append_results(results, design, criterion, payload)

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