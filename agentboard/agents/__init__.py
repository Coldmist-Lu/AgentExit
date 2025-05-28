from .vanilla_agent import VanillaAgent
from .react_style_agent import ReactStyleAgent
from .react_style_agent_verify import ReactStyleAgentVerify
from .react_style_agent_history import ReactStyleAgentHistory
from .react_style_agent_extrinsic_intrinsic import ReactStyleAgentExtrinsicIntrinsic

from common.registry import registry

__all__ = ["VanillaAgent", "ReactStyleAgent", "ReactStyleAgentVerify", "ReactStyleAgentHistory", "ReactStyleAgentExtrinsicIntrinsic"]

def load_agent(name, config, llm_model):
    agent = registry.get_agent_class(name).from_config(llm_model, config)
    return agent
