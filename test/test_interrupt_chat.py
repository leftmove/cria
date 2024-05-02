import unittest

from src import cria

from src.cria import DEFAULT_MESSAGE_HISTORY

ai = cria.Cria()
interruption_length = 5

prompt = "Who is the CEO of OpenAI?"
response = ""
chunks = []
for i, chunk in enumerate(ai.chat(prompt)):
    if i >= interruption_length:
        ai.stop()

    chunks += chunk
    response += chunk
    print(chunk, end="")


class TestChat(unittest.TestCase):
    def test_response(self):
        self.assertIsNot(response, "")

    def test_chunks(self):
        self.assertIsNot(chunks, [])

    def test_interrupt_chat(self):
        self.assertIsNot(ai.messages, DEFAULT_MESSAGE_HISTORY)

    def test_interruption_length(self):
        self.assertIs(len(ai.messages[1]), 0)

    def test_response_length(self):
        self.assertIs(len(response), interruption_length)


if __name__ == "__main__":
    unittest.main()
