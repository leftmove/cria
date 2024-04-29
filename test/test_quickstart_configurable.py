import unittest

from src import cria

with cria.Model() as ai:
    prompt = "Who is the CEO of OpenAI?"
    response = ai.chat(prompt, stream=False)
    print(response)


class TestChat(unittest.TestCase):
    def test_response(self):
        self.assertIsNot(response, "")


if __name__ == "__main__":
    unittest.main()
