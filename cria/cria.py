from typing import Optional

import psutil
import atexit
import subprocess

from ollama._client import Client as OllamaClient
import ollama

DEFAULT_MODEL = "llama3:8b"


class Client(OllamaClient):
    def chat(self, prompt: str, stream: Optional[bool] = True):
        model = self.model
        ai = ollama

        messages = getattr(
            self,
            "messages",
            [{"role": "system", "content": "You are a helpful AI assistant."}],
        )
        messages.append({"role": "user", "content": prompt})

        response = ""

        if stream:
            for chunk in ai.chat(model=model, messages=messages, stream=stream):
                content = chunk["message"]["content"]
                response += content
                yield content
        else:
            response = ai.chat(model=model, messages=messages, stream=stream)
            response = response["message"]["content"]

        messages.append({"role": "assistant", "content": response})
        self.messages = messages

        return response

    def generate(self, prompt: str, stream: Optional[bool] = True):
        model = self.model
        ai = ollama

        response = ""

        if stream:
            for chunk in ai.chat(
                model=model, messages=[{"role": "user", "content": str}], stream=stream
            ):
                response += chunk
                yield chunk
        else:
            response = ai.generate(model=model, prompt=prompt)

        return response

    def clear(self):
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]


class Cria(Client):
    def __init__(
        self,
        model: Optional[str] = DEFAULT_MODEL,
        log_output: Optional[bool] = False,
        run_subprocess: Optional[bool] = False,
        close_on_exit: Optional[bool] = False,
    ) -> None:
        ollama_running = False
        process_name = "ollama"
        for proc in psutil.process_iter():
            try:
                if process_name.lower() in proc.name().lower():
                    ollama_pid = proc.pid
                    ollama_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if ollama_running:
            self.ollama_process = psutil.Process(pid=ollama_pid)
        else:
            self.ollama_process = None

        if ollama_running and run_subprocess:
            self.ollama_process.kill()
            ollama_running = False

        if not ollama_running:
            ollama_stdout = subprocess.PIPE if log_output else subprocess.DEVNULL
            ollama_stderr = subprocess.PIPE if log_output else subprocess.DEVNULL
            self.ollama_subrprocess = subprocess.Popen(
                ["ollama", "serve"], stdout=ollama_stdout, stderr=ollama_stderr
            )
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

    class model(Client, object):
        def __init_subclass__(
            cls,
            model: Optional[str] = DEFAULT_MODEL,
            close_on_exit: Optional[bool] = True,
        ) -> None:
            cls.model = model
            cls.llm = subprocess.Popen(
                ["ollama", "run", model],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            if close_on_exit:
                atexit.register(lambda: cls.llm.kill())

        def __exit__(cls):
            llm = cls.llm
            llm.kill()

        def close(cls):
            llm = cls.llm
            llm.kill()

    def close(self):
        llm = self.llm
        llm.kill()
