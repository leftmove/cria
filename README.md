<p align="center">
  <a href="https://github.com/leftmove/cria"><img src="https://private-user-images.githubusercontent.com/73859069/324219993-741a3c07-da65-4e44-a967-e6e8dcb81920.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTM2NjgxMTYsIm5iZiI6MTcxMzY2NzgxNiwicGF0aCI6Ii83Mzg1OTA2OS8zMjQyMTk5OTMtNzQxYTNjMDctZGE2NS00ZTQ0LWE5NjctZTZlOGRjYjgxOTIwLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA0MjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNDIxVDAyNTAxNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTIyYTlhYzA0ODRkYTQ0ZmQ2MWIwMzc2NTRmYzYzNjA1MzdmNmI2ZDM2YTJiYTZlZGU3NmRkMDhjYTYzY2M1ZDEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.Kd8z9Tyx1XwUOE-riu_zvYXA8D6U0KyKWLFXZNRVgGI" alt="cria"></a>
</p>
<p align="center">
    <em>Cria, use Python to run LLMs with as little friction as possible.</em>
</p>

Cria is a library for programatically running Large Language Models through Python. Cria is built so you need as little configuration as possible — even with more advanced features.

- **Easy**: No configuration is required out of the box. Defaults are built in, so getting started takes just five lines of code.
- **Concise**: Write less code to save time and avoid duplication.
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
  - [Multiple Models and Parallel Conversations](#multiple-models-and-parallel-conversations)
- [Contributing](#contributing)
- [License](#license)

## Quickstart

Running Cria is easy, after installation, you need just five lines of code.

```python
import cria

ai = cria.Cria()

prompt = "Who is the CEO of OpenAI?"
for chunk in ai.chat(prompt):
    print(chunk, end="") # The CEO of OpenAI is Sam Altman!

# Not required, but best practice.
ai.close()
```

By default, Cria runs `llama3:8b`. If `llama3:8b` is not installed on your machine, Cria will install it automatically.

**Important**: If the default model is not installed on your machine, downloading will take a while (`llama:8b` is about 4.7GB).

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

To run other LLM models, pass them into your `ai` variable.

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

### Message History

Message history is automatically saved in Cria, so asking followup questions is easy.

```python
prompt = "Who is the CEO of OpenAI?"
response = ai.chat(prompt, stream=False)
print(response) # The CEO of OpenAI is Sam Altman.

prompt = "Tell me more about him."
response = ai.chat(prompt, stream=False)
print(response) # Sam Altman is an American entrepreneur and technologist who serves as the CEO of OpenAI...
```

Clearing history is available as well.

```python
prompt = "Who is the CEO of OpenAI?"
response = ai.chat(prompt, stream=False)
print(response) # Sam Altman is an American entrepreneur and technologist who serves as the CEO of OpenAI...

ai.clear()

prompt = "Tell me more about him."
response = ai.chat(prompt, stream=False)
print(response) # I apologize, but I don't have any information about "him" because the conversation just started...
```

### Multiple Models and Parallel Conversations

If you are running multiple models or parallel conversations, the `Model` class is also available. This is recommended for most usecases.

```python
import cria

ai = cria.Model()

prompt = "Who is the CEO of OpenAI?"
response = ai.chat(prompt, stream=False)
print(response) # The CEO of OpenAI is Sam Altman.
```

_All methods that apply to the `Cria` class also apply to `Model`._

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

Or they can be run traditonally.

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

Cria can also has a `generate` method.

```python
prompt = "Who is the CEO of OpenAI?"
for chunk in ai.generate(prompt):
    print(chunk, end="") # The CEO of OpenAI (Open-source Artificial Intelligence) is Sam Altman.

promt = "Tell me more about him."
response = ai.generate(prompt, stream=False)
print(response) # I apologize, but I think there may have been some confusion earlier. As this...
```

## Contributing

If you have a feature request, feel free to make an issue!

Contibutions are highly appreciated.

## License

[MIT](./LICENSE.md)
