"""
This script ensures all models listed in the qwen3_models_list are downloaded and accessible.

To access the downloaded models, navigate to the following directory on your Mac:
1. In Finder, press ⌘ + Shift + G (Go to Folder).
2. Paste this path and hit Enter: ~/.cache/huggingface/hub
"""

from matvisor.llm.llama import load_llama
from matvisor.llm.models import qwen3_models_list


for modelsize in qwen3_models_list:
    model = load_llama(modelsize=modelsize)
    print(f"Model of size {modelsize} loaded successfully.")