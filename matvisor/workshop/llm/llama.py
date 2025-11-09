import llama_cpp

from matvisor.workshop.llm.models import qwen3_models as models


def load_llama(modelsize: str = "7") -> llama_cpp.Llama:
    modelsize = str(modelsize)
    return llama_cpp.Llama.from_pretrained(
        repo_id=models[modelsize]["repo_id"],
        filename=models[modelsize]["filename"],
        n_ctx=8192,
        n_gpu_layers=-1,
        verbose=False,
    )


if __name__ == "__main__":
    # <|disable_thought|> should be added to the system prompt to disable internal thoughts
    messages=[
        {"role": "system", "content": "<|disable_thought|>You are an expert materials science tutor."},
        {"role": "user", "content": "Explain what ductility means in less than five sentences."},
    ]
    llama = load_llama("0.6")
    response = llama.create_chat_completion(
        messages=messages,
        max_tokens=500,
        temperature=0.5
    )
    result = response["choices"][0]["message"]["content"]
    # Clean the output by removing any <think> tags if present
    result = result.replace("<think>\n\n</think>\n\n", "").replace("<think>\n</think>\n\n", "")
    print(result)