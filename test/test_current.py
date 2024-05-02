from src import cria

ai = cria.Model(allow_interruption=False)

response = ""
max_token_length = 5

prompt = "Who is the CEO of OpenAI?"
for i, chunk in enumerate(ai.chat(prompt)):
    if i >= max_token_length:
        ai.stop()
        break

    print(chunk, end="")  # The CEO of OpenAI is

prompt = "Tell me more about him."
for chunk in ai.chat(prompt):
    print(
        chunk, end=""
    )  # I apologize, but I don't have any information about "him" because the conversation just started...
