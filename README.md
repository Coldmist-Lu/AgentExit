# AgentExit

<b>Runaway is Ashamed, But Helpful: On the Early-Exit Behavior of Large Language Model-based Agents in Embodied Environments</b>[full paper](https://arxiv.org/pdf/2505.17616)

This repository presents AgentExit, a framework for large language model(LLM)-based agents to early exit when necessary. It is built on [AgentBoard](https://hkust-nlp.github.io/agentboard/), and provide the agent code for replication of the study and as a plug-and-play tool for agent manipulation.

## Abstract

Agents powered by large language models (LLMs) have demonstrated strong planning and decision-making capabilities in complex embodied environments. However, such agents often **suffer from inefficiencies in multi-turn interactions, frequently trapped in repetitive loops or issuing ineffective commands**, leading to redundant computational overhead. Instead of relying solely on learning from trajectories, we take a first step toward exploring the early-exit behavior for LLM-based agents. We propose two complementary approaches: 

<div align="center">
    <img width="90%" alt="image" src="https://github.com/Coldmist-Lu/AgentExit/blob/main/assets/overview.png">
</div>

1. an **intrinsic** method that injects exit instructions during generation,

2. an **extrinsic** method that verifies task completion to determine when to halt an agent's trial.

To evaluate early-exit mechanisms, we introduce two metrics: 

<div align="center">
    <img width="90%" alt="image" src="https://github.com/Coldmist-Lu/AgentExit/blob/main/assets/metrics.png">
</div>

1. **Redundancy Steps**: measures the reduction of redundancy steps as a positive effect,

2. **Progress Degradation**: measures task progress loss via reduced subgoal completion as a negative effect.

Experiments with 4 different LLMs across 5 embodied environments show significant efficiency improvements, with only minor drops in agent performance. We also validate a practical strategy where a stronger agent assists after an early-exit agent, achieving better performance with the same total steps.

## Usage

We provide several different setups, along with the agent and configuration:

| **Intrinsic Early Exit** | **Extrinsic Early Exit** | **Agent** | **Configuration** |
|-------------------------------|---------------------------|----------------------------|-----------------------------|
| ❌ | ❌ | [React Style Agent](./agentboard/agents/react_style_agent.py) | [React Baseline Config](./eval_configs/main_results_all_tasks_lqy_react_baseline.yaml) |
| ✔️ | ❌ | [React Style Agent](./agentboard/agents/react_style_agent.py) | [Intrinsic Config](./eval_configs/main_results_all_tasks_lqy_react_intrinsic.yaml) |
| ❌ | ✔️ | [React Style Verify Agent](./agentboard/agents/react_style_agent_verify.py) | [Intrinsic Config](./eval_configs/main_results_all_tasks_lqy_react_extrinsic.yaml) |
| ✔️ | ✔️ | [React Style Extrinsic+Intrinsic Agent](./agentboard/agents/react_style_agent_extrinsic_intrinsic.py) | [Extrinsic Intrinsic Config](./eval_configs/main_results_all_tasks_lqy_react_extrinsic_intrinsic.yaml) |

We also adjust the datasets task [workflow](./agentboard/tasks/)  (ALFWorld, ScienceWorld, BabyAI, Jericho, PDDL), to permit actions such as "EXIT" to exit the interaction status. We also provide the react style [example](./agentboard/prompts/ReactStyleAgent/). 

## Explanation of Metrics

<div align="center">
    <img width="60%" alt="image" src="https://github.com/Coldmist-Lu/AgentExit/blob/main/assets/interpret-metrics.png">
</div>

Please refer to this picture to explain the behavior of early exit for LLM-based agents.

1. **Perfect Early-Exit Scenario**: The ideal scenario occurs when both RS and PR are zero, meaning no redundant steps and no progress loss.

2. **Too-Early Scenarios**: Reduce redundant steps but significantly impair progress.

3. **Too-Late Scenarios**: PD remains low but RS stays high.

## Experimental Results

<div align="center">
    <img width="70%" alt="image" src="https://github.com/Coldmist-Lu/AgentExit/blob/main/assets/results.png">
</div>

Findings:

1. Early-exit mechanisms significantly **reduce redundant steps**.

2. **Minor performace drop** in success and progress rates.

3. LLMs show **varying preferences** for early exit strategies.

4. **Combining intrinsic and extrinsic** early exit maximizes performance retention.

5. Early-exit strategye **generalizes to gaming environments**.

## Practical Implications

We simulate a practical scenario in embodied environments, where a weaker agent exits early from challenging environments and requests assistance from a stronger agent.

We use ALFWorld as our testset, Mistral-24B-Instruct as the weak agent, and Llama3.1-70B-Instruct as the strong agent.

<div align="center">
    <img width="60%" alt="image" src="https://github.com/Coldmist-Lu/AgentExit/blob/main/assets/practical-implication.png">
</div>

We find that early exit followed by strong agent assistance yields **over a 10% improvement** in success rate within the same 40-step budget.

The implementation of the agent, followed by the other agent history can be seen in [React Style Agent History](./agentboard/agents/react_style_agent_history.py).

## Citation
If you find this work helpful, please consider citing as follows:  

```ruby
@article{Lu2025AgentExit,
  title={Runaway is Ashamed, But Helpful: On the Early-Exit Behavior of Large Language Model-based Agents in Embodied Environments},
  author={Lu, Qingyu and Ding, Liang and Cao, Siyi and Liu, Xuebo and Zhang, Kanjian and Zhang, Jinxia and Tao, Dacheng},
  journal={arXiv preprint},
  url={https://arxiv.org/pdf/2505.17616},
  year={2025}
}
```

