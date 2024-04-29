import unittest
import cria

ai = cria.Cria()

context = "Our AI system employed a hybrid approach combining reinforcement learning and generative adversarial networks (GANs) to optimize the decision-making..."
messages = [
    {"role": "system", "content": "You are a technical documentation writer"},
    {"role": "user", "content": context},
]

prompt = "Write some documentation using the text I gave you. Use only ten words."
response = ""
chunks = []
for chunk in ai.chat(messages=messages, prompt=prompt):
    chunks += chunk
    response += chunk
    print(chunk, end="")


class TestChat(unittest.TestCase):
    def test_response(self):
        self.assertIsNot(response, "")

    def test_chunks(self):
        self.assertIsNot(chunks, [])


if __name__ == "__main__":
    unittest.main()
