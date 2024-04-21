from contextlib import ContextDecorator
from typing import Optional

import psutil
import atexit
import subprocess
import time

from ollama._client import Client as OllamaClient
import ollama

from httpx import ConnectError

DEFAULT_MODEL = "llama3:8b"
DEFAULT_MESSAGE_HISTORY = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]


class Client(OllamaClient):
    def chat_stream(self, messages):
        model = self.model
        ai = ollama

        response = ""

        for chunk in ai.chat(model=model, messages=messages, stream=True):
            content = chunk["message"]["content"]
            response += content
            yield content

        messages.append({"role": "assistant", "content": response})
        self.messages = messages

    def chat(
        self,
        prompt: str,
        messages: Optional[list] = DEFAULT_MESSAGE_HISTORY,
        stream: Optional[bool] = True,
    ) -> str:
        model = self.model
        ai = ollama

        messages = getattr(
            self,
            "messages",
            messages,
        )
        messages.append({"role": "user", "content": prompt})

        if stream:
            return self.chat_stream(messages)

        chunk = ai.chat(model=model, messages=messages, stream=stream)
        response = "".join(chunk["message"]["content"])

        messages.append({"role": "assistant", "content": response})
        self.messages = messages

        return response

    def generate_stream(self, prompt):
        model = self.model
        ai = ollama

        for chunk in ai.generate(model=model, prompt=prompt, stream=True):
            content = chunk["message"]["content"]
            yield content

    def generate(
        self,
        prompt: str,
        stream: Optional[bool] = True,
    ) -> str:
        model = self.model
        ai = ollama

        if stream:
            return self.generate_stream(prompt)

        response = ai.generate(model=model, prompt=prompt, stream=False)
        return response

    def clear(self):
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]


class Model(Client, ContextDecorator):
    def __init__(
        self,
        model: Optional[str] = DEFAULT_MODEL,
        capture_output: Optional[bool] = False,
        run_subprocess: Optional[bool] = False,
        close_on_exit: Optional[bool] = False,
    ) -> None:
        process_name = "ollama"
        ollama_pids = []
        ollama_running = False
        for proc in psutil.process_iter():
            try:
                if process_name.lower() in proc.name().lower():
                    ollama_pids.append(proc.pid)
                    ollama_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if ollama_running:
            self.ollama_pids = ollama_pids
        else:
            self.ollama_pids = None

        if ollama_running and run_subprocess:
            for ollama_pid in self.ollama_pids:
                ollama_process = psutil.Process(pid=ollama_pid)
                ollama_process.kill()
            ollama_running = False

        if not ollama_running:
            ollama_stdout = subprocess.PIPE if capture_output else subprocess.DEVNULL
            ollama_stderr = subprocess.PIPE if capture_output else subprocess.DEVNULL
            self.ollama_subrprocess = subprocess.Popen(
                ["ollama", "serve"], stdout=ollama_stdout, stderr=ollama_stderr
            )
            retries = 10
            while retries:
                try:
                    ollama.list()
                    break
                except ConnectError:
                    time.sleep(1)
                    retries -= 1
        else:
            self.ollama_subrprocess = None

        self.model = model
        self.llm = subprocess.Popen(
            ["ollama", "run", model],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if close_on_exit:
            atexit.register(lambda: self.llm.kill())

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        llm = self.llm
        llm.kill()

    def close(self):
        llm = self.llm
        llm.kill()
