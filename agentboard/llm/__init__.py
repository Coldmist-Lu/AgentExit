from .openai_gpt import OPENAI_GPT
from .azure_gpt import OPENAI_GPT_AZURE
from .claude import CLAUDE
from .vllm import VLLM
from common.registry import registry
from .huggingface import HgModels
from .api_request import API_REQUEST

__all__ = [
    "OPENAI_GPT",
    "OPENAI_GPT_AZURE",
    "VLLM",
    "CLAUDE",
    "HgModels",
    "API_REQUEST",
]





def load_llm(name, config):
    
    llm = registry.get_llm_class(name).from_config(config)
    
    return llm
    
