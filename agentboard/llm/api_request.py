from common.registry import registry
import requests

@registry.register_llm("api_request")
class API_REQUEST:
    def __init__(self,
                 engine="",
                 temperature=0.1,
                 max_tokens=256,
                 system_message="",
                 context_length="4096",
                 return_token=False,
                 base_url="",
                 api_key=""
                 ):

        self.system_message = system_message
        self.context_length = context_length
        self.engine = engine
        self.max_tokens = max_tokens

        self.base_url = base_url
        self.chat_url = self.base_url + 'v1/chat/completions' 
        self.tokenize_url = self.base_url + 'tokenize'
        self.api_key = api_key

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        self.data_template = {
            "model": engine,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        self.tokenizer_template = {
            "model": engine,
        }

        self.return_token = return_token
        
    def llm_inference(self, messages):

        self.data = self.data_template.copy()
        self.data['messages'] = messages

        response = requests.post(url=self.chat_url, headers=self.headers, json=self.data)

        response_dict = response.json()

        return (response_dict['choices'][0]['message']['content'], int(response_dict['usage']['completion_tokens']))

    def generate(self, prompt):

        response, token = self.llm_inference(prompt)

        if self.return_token is True:
            return True, (response, token)
        
        else:
            return True, response

    def num_tokens_from_messages(self, messages):
        """Return the number of tokens used by a list of messages."""

        self.data = self.tokenizer_template.copy()
        self.data['messages'] = messages

        response = requests.post(self.tokenize_url, headers=self.headers, json=self.data)
        response_dict = response.json()

        return response_dict['count']

    @classmethod
    def from_config(cls, config):
        
        engine = config.get("engine", "")
        temperature = config.get("temperature", 0.1)
        max_tokens = config.get("max_tokens", 256)
        system_message = config.get("system_message", "You are a helpful assistant.")
        context_length = config.get("context_length", 4096)
        return_token = config.get("return_token", False)
        
        return cls(engine=engine,
                   temperature=temperature,
                   max_tokens=max_tokens,
                   system_message=system_message,
                   context_length=context_length,
                   return_token=return_token)
