from contextlib import ContextDecorator
from typing import Optional

import psutil
import atexit
import subprocess
import time

from ollama._client import Client as OllamaClient
import ollama

from httpx import ConnectError, ReadError

DEFAULT_MODEL = "llama3:8b"
DEFAULT_MESSAGE_HISTORY = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]


def check_models(model, silence_output):
    model_list = ollama.list().get("models", [])
    for m in model_list:
        m_name = m.get("name", "")
        if m_name == model:
            return model
        if model in m_name:
            m_without_version = next(iter(m_name.split(":")), "")
            if model == m_without_version:
                if not silence_output:
                    print(f"LLM model found, running {m_name}...")
                return m_name
            else:
                if not silence_output:
                    print(f"LLM partial match found, running {m_name}...")
                return m_name
    model_match = next(
        (True if m.get("name") == model else False for m in model_list), False
    )
    if model_match:
        return

    if not silence_output:
        print(f"LLM model not found, searching '{model}'...")

    try:
        progress = ollama.pull(model, stream=True)
        print(
            f"LLM model {model} found, downloading... (this will probably take a while)"
        )
        if not silence_output:
            for chunk in progress:
                print(chunk)
            print(f"'{model}' downloaded, starting processes.")
        return model
    except Exception as e:
        print(e)
        raise ValueError(
            "Invalid model passed. See the model library here: https://ollama.com/library"
        )


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
            content = chunk["response"]
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

        chunk = ai.generate(model=model, prompt=prompt, stream=False)
        response = chunk["response"]

        return response

    def clear(self):
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]


class Cria(Client):
    def __init__(
        self,
        model: Optional[str] = DEFAULT_MODEL,
        run_subprocess: Optional[bool] = False,
        run_llm: Optional[bool] = True,
        capture_output: Optional[bool] = False,
        silence_output: Optional[bool] = False,
        close_on_exit: Optional[bool] = True,
    ) -> None:
        self.run_subprocess = run_subprocess
        self.capture_output = capture_output
        self.silence_output = silence_output
        self.close_on_exit = close_on_exit

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

        try:
            ollama.list()
        except (ConnectError, ReadError):
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
                except (ConnectError, ReadError):
                    time.sleep(2)
                    retries -= 1
        else:
            self.ollama_subrprocess = None

        model = check_models(model, silence_output)
        self.model = model

        if run_llm:
            self.llm = subprocess.Popen(
                ["ollama", "run", model],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if close_on_exit and self.ollama_subrprocess:
            atexit.register(lambda: self.ollama_subrprocess.kill())

        if close_on_exit and run_llm:
            atexit.register(lambda: self.llm.kill())

    def output(self):
        ollama_subprocess = self.ollama_subrprocess
        if not ollama_subprocess:
            raise ValueError(
                "Ollama is not running as a subprocess, you must pass run_subprocess as True to capture output."
            )
        if not self.capture_output:
            raise ValueError(
                "You must pass in capture_ouput as True to capture output."
            )

        return iter(lambda: ollama_subprocess.stdout.read(1), "")

    def close(self):
        llm = self.llm
        llm.kill()


class Model(Cria, ContextDecorator):
    def __init__(
        self,
        model: Optional[str] = DEFAULT_MODEL,
        capture_output: Optional[bool] = False,
        silence_output: Optional[bool] = False,
        close_on_exit: Optional[bool] = True,
    ) -> None:
        super().__init__(
            model=model,
            capture_output=capture_output,
            run_subprocess=True if capture_output else False,
            run_llm=False,
            close_on_exit=close_on_exit,
        )

        self.capture_output = capture_output
        self.silence_output = silence_output
        self.close_on_exit = close_on_exit

        llm_stdout = subprocess.PIPE if capture_output else subprocess.DEVNULL
        llm_stderr = subprocess.PIPE if capture_output else subprocess.DEVNULL
        self.llm = subprocess.Popen(
            ["ollama", "run", model], stdout=llm_stdout, stderr=llm_stderr
        )

        if close_on_exit:
            atexit.register(lambda: self.llm.kill())

    def capture_output(self):
        if not self.capture_output:
            raise ValueError(
                "You must pass in capture_ouput as True to capture output."
            )

        return iter(lambda: self.llm.stdout.read(1), "")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        llm = self.llm
        llm.kill()
