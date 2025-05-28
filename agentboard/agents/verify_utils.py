import json
import re
from typing import List, Tuple

def convert_json2list(output: str):
    """json file -> list"""
    match = re.search(r'\[\s*[\s\S]*\s*\]', output)
    if match:
        json_str = match.group(0)  # 提取匹配的 JSON 字符串
        data_list = json.loads(json_str)  # 解析 JSON
        return data_list
    else:
        print("No JSON found")

def convert_memory2str(memory: List[Tuple[str, str]]):
    """convert memory list to string"""

    return "\n".join(f"{mem[0]}: {mem[1]}" if mem[0] != "Action" else mem[1] for mem in memory)
    

VERIFY_PROMPT = {
    "modest": """
Evaluate the agent’s recent history and consider:
	1.	Whether the agent appears stuck or making little meaningful progress despite repeated attempts.
	2.	Whether the task seems complete or no longer feasible to pursue.

If you have good reason to believe further steps are unlikely to help, you may output “YES” to suggest stopping. Otherwise, output “NO” and continue exploring."
""",

    "strict": """
Evaluate the current history of the agent’s actions and determine if it meets any of the following conditions:
	1.	The recent steps show repetitive actions or the agent appears to be stuck in a loop.
 	2.	The agent repeatedly checks for valid actions but fails to make meaningful progress toward the objective.
	3.	The agent’s recent actions suggest the task is complete and no further steps are necessary.
 	4.	The task is no longer achievable due to high difficulty or significant deviation from the expected course.

If any of the above conditions are met, output “YES”. Otherwise, output “NO” to indicate the agent should continue exploring.
"""
}


class Verify():

    def __init__(self, llm_model, verify_format="strict"):
        self.llm_model = llm_model
        self.token_cnt = 0 # means the token cnt per scenario , not task total.
        self.verify_format = verify_format
        assert self.verify_format in ['modest', 'strict']

    def _prompt_verify_easy(self, instruction: str, goal: str, history_str: str):
        """测试当前 checklist goal 是否已经完成。"""

        return f"""
You will be given a historical scenario in which you are placed in a specific environment with a designated objective to accomplish.  

### Task Description:  
{instruction}  

### Your Objective:
{goal}  

### Your Current History:
{convert_memory2str(history_str)}

### Instructions:
{VERIFY_PROMPT[self.verify_format]}

Include a short explanation in your response.

"""

    def init_verify(self, ):
        self.exit_flag = False
    
    def verify(self, sys_mess, instruction, goal, memory, step_id):
        
        prompt = self._prompt_verify_easy(instruction, goal, memory)
        message = [
            {"role": "system", "content": sys_mess},
            {"role": "user", "content": prompt}
        ]
        _, response = self.llm_model.generate(message)

        if isinstance(response, tuple):
            self.token_cnt += response[-1]
            response = response[0]

        if "YES" in response:
            self.exit_flag = True
            return