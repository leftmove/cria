import unittest

from src import cria

ai = cria.Cria()
interruption_length = 5

prompt = "Who is the CEO of OpenAI?"
response = ""
chunks = []

for i, chunk in enumerate(ai.chat(prompt)):
    chunks += chunk
    response += chunk
    print(chunk, end="")

    if i >= interruption_length:
        ai.stop()


class TestChat(unittest.TestCase):
    def test_response(self):
        self.assertIsNot(response, "")

    def test_chunks(self):
        self.assertIsNot(chunks, [])

    def test_interruption_length(self):
        self.assertIsNot(len(ai.messages[-1]["content"]), 0)

    def test_response_length(self):
        self.assertIs(i, interruption_length)


if __name__ == "__main__":
    unittest.main()
