qwen3_models = {
    "0.6": {
        "repo_id": "Qwen/Qwen3-0.6B-GGUF",
        "filename": "Qwen3-0.6B-Q8_0.gguf",
    },
    "1.7": {
        "repo_id": "Qwen/Qwen3-1.7B-GGUF",
        "filename": "Qwen3-1.7B-Q8_0.gguf",
    },
    "4": {
        "repo_id": "Qwen/Qwen3-4B-GGUF",
        "filename": "Qwen3-4B-Q8_0.gguf",
    },
    "8": {
        "repo_id": "Qwen/Qwen3-8B-GGUF",
        "filename": "Qwen3-8B-Q8_0.gguf",
    },
    "14": {
        "repo_id": "Qwen/Qwen3-14B-GGUF",
        "filename": "Qwen3-14B-Q8_0.gguf",
    },
    "32": {
        "repo_id": "Qwen/Qwen3-32B-GGUF",
        "filename": "Qwen3-32B-Q8_0.gguf",
    },
}

qwen3_models_list = list(qwen3_models.keys())


if __name__ == "__main__":
    print("Available models: ", qwen3_models_list)