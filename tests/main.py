# Quick Start

import sys

sys.path.append("../")

from src import cria

ai = cria.Cria()

prompt = "Who is the CEO of OpenAI?"
for chunk in ai.generate(prompt):
    print(chunk, end="")
    # OpenAI, a non-profit artificial intelligence research organization, does...

prompt = "Tell me more about him."
response = ai.generate(prompt, stream=False)
print(response)
