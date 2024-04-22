# Quick Start

import sys

sys.path.append("../")

from src import cria

ai = cria.Cria()


context = "Our AI system employed a hybrid approach combining reinforcement learning and generative adversarial networks (GANs) to optimize the decision-making..."
messages = [
    {"role": "system", "content": "You are a technical documentation writer"},
    {"role": "user", "content": context},
]

prompt = "Write some documentation using the text I gave you."
for chunk in ai.chat(messages=messages, prompt=prompt):
    print(
        chunk, end=""
    )  # AI System Optimization: Hybrid Approach Combining Reinforcement Learning and...
