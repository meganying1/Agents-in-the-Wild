"""
This script ensures all models listed in the qwen3_models_list are downloaded and accessible.
If any of the models are not present locally, they will be downloaded automatically.

-----------------------------------------
Where the models are stored (default paths)
-----------------------------------------

Hugging Face stores cached models under:
- macOS:  ~/.cache/huggingface/hub
- Linux:  ~/.cache/huggingface/hub
- Windows: %USERPROFILE%\\.cache\\huggingface\\hub
(If the environment variable HF_HOME is set, the cache is at: $HF_HOME/hub)

-----------------------------------------
How to open the folder
-----------------------------------------

macOS (Finder):
1) Press ⌘ + Shift + G
2) Paste: ~/.cache/huggingface/hub
3) Enter

Linux (Terminal / File Manager):
- Terminal:  cd ~/.cache/huggingface/hub
- File manager (most desktops): run `xdg-open ~/.cache/huggingface/hub`

Windows (File Explorer / PowerShell):
- File Explorer address bar:  %USERPROFILE%\\.cache\\huggingface\\hub
- PowerShell:
    cd "$env:USERPROFILE\\.cache\\huggingface\\hub"
    ii "$env:USERPROFILE\\.cache\\huggingface\\hub"   # 'ii' = Invoke-Item opens the folder
"""

from matvisor.llm.llama import load_llama
from matvisor.llm.models import qwen3_models_list


for modelsize in qwen3_models_list:
    model = load_llama(modelsize=modelsize)
    print(f">>> Model of size {modelsize}B parameters loaded successfully.")