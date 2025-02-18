<p align="center">
  <a href="https://github.com/leftmove/cria"><img src="https://i.imgur.com/vjGJOLQ.png" alt="cria"></a>
</p>
<p align="center">
    <em>Cria, use Python to run LLMs with as little friction as possible.</em>
</p>

Cria is a library for programmatically running Large Language Models through Python. Cria is built so you need as little configuration as possible — even with more advanced features.

- **Easy**: No configuration is required out of the box. Getting started takes just five lines of code.
- **Concise**: Write less code to save time and avoid duplication.
- **Local**: Free and unobstructed by rate limits, running LLMs requires no internet connection.
- **Efficient**: Use advanced features with your own `ollama` instance, or a subprocess.

<!-- <p align="center">
  <em>
    Cria uses <a href="https://ollama.com/">ollama</a>.
  </em>
</p> -->

## Guide

- [Quick Start](#quickstart)
- [Installation](#installation)
  - [Windows](#windows)
  - [Mac](#mac)
  - [Linux](#linux)
- [Advanced Usage](#advanced-usage)
  - [Custom Models](#custom-models)
  - [Streams](#streams)
  - [Closing](#closing)
  - [Message History](#message-history)
    - [Follow-Up](#follow-up)
    - [Clear Message History](#clear-message-history)
    - [Passing In Custom Context](#passing-in-custom-context)
  - [Interrupting](#interrupting)
    - [With Message History](#with-message-history)
    - [Without Message History](#without-message-history)
  - [Multiple Models and Parallel Conversations](#multiple-models-and-parallel-conversations)
    - [Models](#models)
    - [With](#with-model)
    - [Standalone](#standalone-model)
  - [Running Standalone](#running-standalone)
  - [Formatting](#formatting)
- [Contributing](#contributing)
- [License](#license)

## Quickstart

Running Cria is easy. After installation, you need just five lines of code — no configurations, no manual downloads, no API keys, and no servers to worry about.

```python
import cria

ai = cria.Cria()

prompt = "Who is the CEO of OpenAI?"
for chunk in ai.chat(prompt):
    print(chunk, end="")
```

```
>>> The CEO of OpenAI is Sam Altman!
```

or, you can run this more configurable example.

```python
import cria

with cria.Model("llama3.1:8b") as ai:
  prompt = "Who is the CEO of OpenAI?"
  response = ai.chat(prompt, stream=False)
  print(response)

with cria.Model("llama3:8b") as ai:
  prompt = "Who is the CEO of OpenAI?"
  response = ai.chat(prompt, stream=False)
  print(response)
```

```
>>> The CEO of OpenAI is Sam Altman.
>>> The CEO of OpenAI is Sam Altman!
```

> [!WARNING]
> If no model is configured, Cria automatically installs and runs the default model: `llama3.1:8b` (4.7GB).

## Installation

1. Cria uses [`ollama`](https://ollama.com/), to install it, run the following.

   ### Windows

   [Download](https://ollama.com/download/windows)

   ### Mac

   [Download](https://ollama.com/download/mac)

   ### Linux

   ```
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Install Cria with `pip`.

   ```
   pip install cria
   ```

## Advanced Usage

### Custom Models

To run other LLMs, pass them into your `ai` variable.

```python
import cria

ai = cria.Cria("llama2")

prompt = "Who is the CEO of OpenAI?"
for chunk in ai.chat(prompt):
    print(chunk, end="") # The CEO of OpenAI is Sam Altman. He co-founded OpenAI in 2015 with...
```

You can find available models [here](https://ollama.com/library).

### Streams

Streams are used by default in Cria, but you can turn them off by passing in a boolean for the `stream` parameter.

```python
prompt = "Who is the CEO of OpenAI?"
response = ai.chat(prompt, stream=False)
print(response) # The CEO of OpenAI is Sam Altman!
```

### Closing

By default, models are closed when you exit the Python program, but closing them manually is a best practice.

```python
ai.close()
```

You can also use [`with`](#with-model) statements to close models automatically (recommended).

### Message History

#### Follow-Up

Message history is automatically saved in Cria, so asking follow-up questions is easy.

```python
prompt = "Who is the CEO of OpenAI?"
response = ai.chat(prompt, stream=False)
print(response) # The CEO of OpenAI is Sam Altman.

prompt = "Tell me more about him."
response = ai.chat(prompt, stream=False)
print(response) # Sam Altman is an American entrepreneur and technologist who serves as the CEO of OpenAI...
```

#### Clear Message History

You can reset message history by running the `clear` method.

```python
prompt = "Who is the CEO of OpenAI?"
response = ai.chat(prompt, stream=False)
print(response) # Sam Altman is an American entrepreneur and technologist who serves as the CEO of OpenAI...

ai.clear()

prompt = "Tell me more about him."
response = ai.chat(prompt, stream=False)
print(response) # I apologize, but I don't have any information about "him" because the conversation just started...
```

#### Passing In Custom Context

You can also create a custom message history, and pass in your own context.

```python
context = "Our AI system employed a hybrid approach combining reinforcement learning and generative adversarial networks (GANs) to optimize the decision-making..."
messages = [
    {"role": "system", "content": "You are a technical documentation writer"},
    {"role": "user", "content": context},
]

prompt = "Write some documentation using the text I gave you."
for chunk in ai.chat(messages=messages, prompt=prompt):
    print(chunk, end="") # AI System Optimization: Hybrid Approach Combining Reinforcement Learning and...
```

In the example, instructions are given to the LLM as the `system`. Then, extra context is given as the `user`. Finally, the prompt is entered (as a `user`). You can use any mixture of roles to specify the LLM to your liking.

The available roles for messages are:

- `user` - Pass prompts as the user.
- `system` - Give instructions as the system.
- `assistant` - Act as the AI assistant yourself, and give the LLM lines.

The prompt parameter will always be appended to messages under the `user` role, to override this, you can choose to pass in nothing for `prompt`.

### Interrupting

#### With Message History

If you are streaming messages with Cria, you can interrupt the prompt mid way.

```python
response = ""
max_token_length = 5

prompt = "Who is the CEO of OpenAI?"
for i, chunk in enumerate(ai.chat(prompt)):
  if i >= max_token_length:
    ai.stop()
  response += chunk

print(response) # The CEO of OpenAI is
```

```python
response = ""
max_token_length = 5

prompt = "Who is the CEO of OpenAI?"
for i, chunk in enumerate(ai.generate(prompt)):
  if i >= max_token_length:
    ai.stop()
  response += chunk

print(response) # The CEO of OpenAI is
```

In the examples, after the AI generates five tokens (units of text that are usually a couple of characters long), text generation is stopped via the `stop` method. After `stop` is called, you can safely `break` out of the `for` loop.

#### Without Message History

By default, Cria automatically saves responses in message history, even if the stream is interrupted. To prevent this behaviour though, you can pass in the `allow_interruption` boolean.

```python
ai = cria.Cria(allow_interruption=False)

response = ""
max_token_length = 5

prompt = "Who is the CEO of OpenAI?"
for i, chunk in enumerate(ai.chat(prompt)):

  if i >= max_token_length:
    ai.stop()
    break

  print(chunk, end="") # The CEO of OpenAI is

prompt = "Tell me more about him."
for chunk in ai.chat(prompt):
  print(chunk, end="") # I apologize, but I don't have any information about "him" because the conversation just started...
```

### Multiple Models and Parallel Conversations

#### Models

If you are running multiple models or parallel conversations, the `Model` class is also available. This is recommended for most use cases.

```python
import cria

ai = cria.Model()

prompt = "Who is the CEO of OpenAI?"
response = ai.chat(prompt, stream=False)
print(response) # The CEO of OpenAI is Sam Altman.
```

_All methods that apply to the `Cria` class also apply to `Model`._

#### With Model

Multiple models can be run through a `with` statement. This automatically closes them after use.

```python
import cria

prompt = "Who is the CEO of OpenAI?"

with cria.Model("llama3") as ai:
  response = ai.chat(prompt, stream=False)
  print(response) # OpenAI's CEO is Sam Altman, who also...

with cria.Model("llama2") as ai:
  response = ai.chat(prompt, stream=False)
  print(response) # The CEO of OpenAI is Sam Altman.
```

#### Standalone Model

Or, models can be run traditionally.

```python
import cria


prompt = "Who is the CEO of OpenAI?"

llama3 = cria.Model("llama3")
response = llama3.chat(prompt, stream=False)
print(response) # OpenAI's CEO is Sam Altman, who also...

llama2 = cria.Model("llama2")
response = llama2.chat(prompt, stream=False)
print(response) # The CEO of OpenAI is Sam Altman.

# Not required, but best practice.
llama3.close()
llama2.close()

```

### Generate

Cria also has a `generate` method.

```python
prompt = "Who is the CEO of OpenAI?"
for chunk in ai.generate(prompt):
    print(chunk, end="") # The CEO of OpenAI (Open-source Artificial Intelligence) is Sam Altman.

promt = "Tell me more about him."
response = ai.generate(prompt, stream=False)
print(response) # I apologize, but I think there may have been some confusion earlier. As this...
```

### Running Standalone

When you run `cria.Cria()`, an `ollama` instance will start up if one is not already running. When the program exits, this instance will terminate.

However, if you want to save resources by not exiting `ollama`, either run your own `ollama` instance in another terminal, or run a managed subprocess.

#### Running Your Own Ollama Instance

```bash
ollama serve
```

```python
prompt = "Who is the CEO of OpenAI?"
with cria.Model() as ai:
    response = ai.generate("Who is the CEO of OpenAI?", stream=False)
    print(response)
```

#### Running A Managed Subprocess (Reccomended)

```python

# If it is the first time you start the program, ollama will start automatically
# If it is the second time (or subsequent times) you run the program, ollama will already be running

ai = cria.Cria(standalone=True, close_on_exit=False)
prompt = "Who is the CEO of OpenAI?"

with cria.Model("llama2") as llama2:
    response = llama2.generate("Who is the CEO of OpenAI?", stream=False)
    print(response)

with cria.Model("llama3") as llama3:
    response = llama3.generate("Who is the CEO of OpenAI?", stream=False)
    print(response)

quit()
# Despite exiting, olama will keep running, and be used the next time this program starts.
```

### Formatting

To format the output of the LLM, pass in the format keyword.

```python
ai = cria.Cria()

prompt = "Return a JSON array of AI companies."
response = ai.chat(prompt, stream=False, format="json")
print(response) # ["OpenAI", "Anthropic", "Meta", "Google", "Cohere", ...].
```

The current supported formats are:

* JSON 

## Contributing

If you have a feature request, feel free to make an issue!

Contributions are highly appreciated.

## License

[MIT](./LICENSE.md)
