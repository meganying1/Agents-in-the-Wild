import os
import llama_cpp
from huggingface_hub import hf_hub_download
from contextlib import redirect_stderr

from matvisor.llm.models import qwen3_models as models


def load_llama(modelsize: str = "7") -> llama_cpp.Llama:

    # Choices are: "INFO", "WARN", "ERROR", "NONE"
    os.environ["GGML_LOG_LEVEL"] = "NONE"
    os.environ["LLAMA_LOG_LEVEL"] = "NONE"

    modelsize = str(modelsize)
    repo_id  = models[modelsize]["repo_id"]
    filename = models[modelsize]["filename"]

    # 1) Download first — progress is shown by default in terminal
    #    (progress goes to stderr; we are NOT redirecting here)
    model_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        force_download=False,
        # To hide progress, you could set local_files_only=True or capture stderr,
        # but we want it visible here.
    )

    # 2) Now suppress native backend noise ONLY during model init
    with open(os.devnull, "w") as devnull, redirect_stderr(devnull):
        llm = llama_cpp.Llama(
            model_path=model_path,
            n_ctx=8192,
            n_gpu_layers=-1,
            verbose=False,
        )

    return llm


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