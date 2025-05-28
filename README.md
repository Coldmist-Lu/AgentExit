# AgentExit

<b>Runaway is Ashamed, But Helpful: On the Early-Exit Behavior of Large Language Model-based Agents in Embodied Environments</b>

This repository presents AgentExit, a framework for large language model(LLM)-based agents to early exit when necessary. It is built on [AgentBoard](https://hkust-nlp.github.io/agentboard/), and provide the agent code for replication of the study and as a plug-and-play tool for agent manipulation.

## Abstract

Agents powered by large language models (LLMs) have demonstrated strong planning and decision-making capabilities in complex embodied environments. However, such agents often suffer from inefficiencies in multi-turn interactions, frequently trapped in repetitive loops or issuing ineffective commands, leading to redundant computational overhead. Instead of relying solely on learning from trajectories, we take a first step toward exploring the early-exit behavior for LLM-based agents. We propose two complementary approaches: 

<div align="center">
    <img width="80%" alt="image" src="https://github.com/Coldmist-Lu/MQM_APE/blob/main/assets/overview.png">
</div>

1. an **intrinsic** method that injects exit instructions during generation,

2. an **extrinsic** method that verifies task completion to determine when to halt an agent's trial.

To evaluate early-exit mechanisms, we introduce two metrics: 

<div align="center">
    <img width="80%" alt="image" src="https://github.com/Coldmist-Lu/MQM_APE/blob/main/assets/metrics.png">
</div>

1. **Redundancy Steps**: measures the reduction of redundancy steps as a positive effect,

2. **Progress Degradation**: measures task progress loss via reduced subgoal completion as a negative effect.

Experiments with 4 different LLMs across 5 embodied environments show significant efficiency improvements, with only minor drops in agent performance. We also validate a practical strategy where a stronger agent assists after an early-exit agent, achieving better performance with the same total steps.

## Usage

We provide 3 different steps.
