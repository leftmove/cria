import unittest

from src import cria

ai = cria.Cria()

prompt = "Who is the CEO of OpenAI?"
response = ""
chunks = []
for chunk in ai.chat(prompt):
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
