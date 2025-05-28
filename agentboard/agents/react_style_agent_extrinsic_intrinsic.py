from agents.base_agent import BaseAgent
from common.registry import registry
from .verify_utils import Verify
import re
import json

INTRINSIC_PROMPT = {
    "short_thought": "\n**Note**: Your thought should be short, clear and concise.", # not using early-exit, but make the thought short as baseline.
    "exit_modest": "\n**Note**: Your thought should be short, clear and concise. If you believe the environment is complete, your task is finished, and no further attempts are needed, please include 'EXIT' in your action.",
    "exit_strict":  "\n**Note**: Your thought should be short, clear and concise. Once the environment appears complete or no further progress is likely, include 'EXIT' in your action to end the task without delay.",
}

@registry.register_agent("ReactStyleAgentExtrinsicIntrinsic") # Agent with react format
class ReactStyleAgentExtrinsicIntrinsic(BaseAgent):  # the agent should receive goal, state and action, then return the next state
    def __init__(self,
                 llm_model,
                 memory_size=100,
                 # set this to a very large number if you want to keep all history till context length limit
                 examples=[],
                 instruction="",
                 init_prompt_path=None,
                 system_message="You are a helpful assistant.",
                 need_goal=False,
                 check_actions=None,
                 check_inventory=None,
                 use_parser=True,
                 intrinsic_exit="short_thought",
                 extrinsic_exit=None,
                 extrinsic_iter=1,
                 ):
        super().__init__()
        self.use_parser = use_parser
        self.llm_model = llm_model
        self.memory_size = memory_size
        self.goal = None
        self.init_obs = None
        if init_prompt_path is not None:  # load from file
            self.init_prompt_dict = json.load(open(init_prompt_path, 'r'))
            self.instruction = self.init_prompt_dict["instruction"]
            self.examples = self.init_prompt_dict["examples"]
            self.system_message = self.init_prompt_dict["system_msg"]
        else:
            self.instruction = instruction
            self.examples = examples

            # self.reset(goal, init_obs)
            self.init_prompt_dict = {
                "examples": examples,
                "instruction": instruction,
                "system_msg": system_message
            }
            self.system_message = system_message

        self.max_context_length = self.llm_model.context_length
        self.need_goal = need_goal
        self.check_actions = check_actions
        self.check_inventory = check_inventory
        # self.max_think_iters = max_think_iters
        self.force_action = False   # Sometimes the agent does not generate action or think, we need to force it to take action.
        self.intrinsic_exit = intrinsic_exit
        assert self.intrinsic_exit in [None, "short_thought", "exit_modest", "exit_strict"], "intrinsic_exit is not available."

        self.extrinsic_exit = extrinsic_exit
        if self.extrinsic_exit is not None:
            self.extrinsic_tool = Verify(llm_model, verify_format=extrinsic_exit)
            self.extrinsic_iter = extrinsic_iter

        if "claude" in self.llm_model.engine:
            self.split = self.llm_model.xml_split
        else:
            self.split = {"example": [""],
                          "text": [""],
                          "rule": [""],
                          "system_msg": [""],
                          "instruction": [""],
                          "goal": [""]}

    def reset(self, goal, init_obs, init_act=None, env=None):
        self.goal = goal
        self.init_obs = init_obs
        self.memory = [("Action", init_act), ('Observation', self.init_obs)] if init_act \
            else [
            ('Observation', self.init_obs)]  # list of [('State', "xxx"), ('Action', "xxx"), ...] # init_act is None for all game and embodied AI tasks.
        self.steps = 0
        self.done = False
        self.env = env # init env
        # checklist reset
        if self.extrinsic_exit is not None:
            self.extrinsic_tool.init_verify()
            self.intrinsic_using_flag = False


    def extract_think_action(self, response: str):
        # 使用正则提取 Think 和 Action 内容
        match = re.search(r"\s*Thought:\s*(.*?)\s*Action:\s*(.*)", response, re.DOTALL)
        if match:
            think = match.group(1).strip()
            action_full = match.group(2).strip()
            # 只取 Action 内容的第一行
            action = action_full.split('\n')[0].strip()
            return think, action
        else:
            return None, None

    def update(self, action='', state=''):
        self.steps += 1
        # self.memory.append(("Action", action))
        self.memory.append(("Observation", state))

        if self.extrinsic_exit is not None:
            if self.steps % self.extrinsic_iter == 0:
                self.extrinsic_tool.verify(self.system_message, self.instruction, self.goal, self.memory, self.steps-1)

    def make_prompt(self,
                    need_goal=False,
                    check_actions="check valid actions",
                    check_inventory="inventory",
                    system_message=""):

        instruction_str = self.split["instruction"][0] + self.instruction + self.split["instruction"][-1]
        
        self.system_message = system_message

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": instruction_str},
            {"role": "assistant", "content": "OK"},
        ]

        for idx in range(0, len(self.examples), 2): # add examples in messages
            messages.append({"role": "user", "content": self.examples[idx]})
            if idx + 1 < len(self.examples):
                messages.append({"role": "assistant", "content": self.examples[idx + 1]})

        if messages[-1]['role'] == "user": # observation comes last
            messages.append({"role": "assistant", "content": "OK"})

        # init query
        query = ""
        if need_goal:
            query += "Now, it's your turn. You should perform thoughts and actions to accomplish the goal. Your response should use the following format:\n\nThought: <your thoughts>\nAction: <your next action>\n\nYour task is: " + self.goal + "\n"

        history = self.memory[-self.memory_size:]

        if history[0][0] == "Observation":
            query += history[0][1]

        messages.append({"role": "user", "content": query})

        # history message
        history_message = []
        for _h in history[1:]:
            if _h[0] == "Action": # performed by LLMs
                history_message.append({"role": "assistant", "content": _h[1]})
            elif _h[0] == "Observation": # performed by Envs
                history_message.append({"role": "user", "content": _h[1]})
        # cut history if out of length
        num_of_tokens = self.llm_model.num_tokens_from_messages(messages + history_message)
        while num_of_tokens > self.max_context_length - self.llm_model.max_tokens:
            history_message = history_message[2:]
            num_of_tokens = self.llm_model.num_tokens_from_messages(messages + history_message)
        
        prompt_message = messages + history_message

        # add early_exit
        if self.intrinsic_exit is not None and self.intrinsic_using_flag is True:
            prompt_message[-1]['content'] += INTRINSIC_PROMPT[self.intrinsic_exit]
        else:
            prompt_message[-1]['content'] += INTRINSIC_PROMPT["thought_short"]
        
        # command help
        commands_helplist = []
        if check_actions is not None:
            commands_helplist.append(f"\"{check_actions}\"")
        if check_inventory is not None:
            commands_helplist.append(f"\"inventory\"")

        if self.env is None:
            prompt_message[-1]['content'] += "\nYou should use the following commands for help when your action cannot be understood: " + " ".join(commands_helplist)
        else:
            # get commands
            commands_list = self.env.get_action_space()
            prompt_message[-1]['content'] += "\nThe next action could be chosen from these valid actions: " + ", ".join(commands_list)

        return prompt_message


    def action_parser_for_special_llms(self, action):
        
        '''
        This function is used to parse the action for special llms, e.g. codellama-13b, codellama-34b, llama, lemur, vicuna, etc.
        These llms often struggle to generate the format of the action correctly, so we need to parse the action to make it executable.
        '''
        
        origin_action = action
        if 'action' in action.lower():
            action_temp = action.split('\n')
            for act in action_temp:
                # if "next action" in act and ':' in act: # zzh: in Claude will return "Here is the next action to take:"
                #     idx = action_temp.index(act)
                #     while idx + 1 < len(action_temp):
                #         if action_temp[idx + 1]:
                #             action = action_temp[idx + 1]
                #             break
                #         idx += 1
                # if act.split(':')[0].lower().endswith('with action input'): # chang: in case parse tool output
                #     action = act
                #     break
                try:

                    if 'action' in act.lower() and ':' in act:
                        action_temp = ':'.join(act.split(':')[1:])
                        if action_temp != "":
                            action = action_temp
                            break
                    if 'action' in act.lower() and 'is to' in act:
                        action_temp = act.split('is to')[1]
                        if action_temp != "":
                            action = action_temp
                            break
                
                except:
                    continue
                        
        if action.strip() == "":
            action = origin_action.split('\n')[0]   # temperary comment this line for codellama
        action = action.strip()
        action = action.strip("'/")
        action = action.split('\n')[0]
        return action

    def run(self, init_prompt_dict=None):

        # note that these configs are originally provided when initialized, but you can choose to override them here with parameters
        if init_prompt_dict is not None:
            self.init_prompt_dict = init_prompt_dict
            self.instruction = init_prompt_dict['instruction']
            self.examples = init_prompt_dict['examples']
        system_message = self.init_prompt_dict['system_msg']

        if self.extrinsic_exit is not None and self.extrinsic_tool.exit_flag is True:
            self.intrinsic_using_flag = True

        input_message = self.make_prompt(need_goal=self.need_goal,
                                        check_actions=self.check_actions,
                                        check_inventory=self.check_inventory,
                                        system_message=system_message)
        
        token_cnt = None

        for _iter in range(3):

            success, response = self.llm_model.generate(input_message)

            if isinstance(response, tuple):
                token_cnt = response[-1]
                response = response[0]
                
            try:
                thought, action = self.extract_think_action(response)
                if self.use_parser:
                    action = self.action_parser_for_special_llms(action)

                break

            except Exception as e:
                print(f"Exception: {e}")
                print(f"Invalid Generation detected: {response}")
                continue

        else:
            # the thought and action is not detected. Trivial return.
            thought = "Invalid Generation."
            action = self.check_actions if self.check_actions is not None else "None"

        self.memory.append(
            ("Action", f"Thought: {thought}\nAction: {action}")
        )

        action_dict = {
            "response": response,
            "thought": thought,
            "action": action,
            "token": token_cnt
        }

        return success, action_dict

    @classmethod
    def from_config(cls, llm_model, config):
        memory_size = config.get("memory_size", 100)
        instruction = config.get("instruction", "")
        examples = config.get("examples", [])
        init_prompt_path = config.get("init_prompt_path", None)
        system_message = config.get("system_message", "You are a helpful assistant.")
        check_actions = config.get("check_actions", None)
        check_inventory = config.get("check_inventory", None)
        use_parser = config.get("use_parser", True)
        need_goal = config.get("need_goal", False)
        intrinsic_exit = config.get("intrinsic_exit", "short_thought")
        extrinsic_exit = config.get("extrinsic_exit", None)
        extrintic_iter = config.get("extrintic_iter", 1)

        return cls(llm_model, memory_size, examples, instruction, init_prompt_path, system_message, 
                   need_goal, check_actions, check_inventory, use_parser, intrinsic_exit, extrinsic_exit, extrintic_iter) 
