from contextlib import ContextDecorator
from typing import Optional

import psutil
import atexit
import subprocess
import time

import ollama
import httpx

from ollama._client import Client as OllamaClient

DEFAULT_MODEL = "llama3:8b"
DEFAULT_MESSAGE_HISTORY = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]


class Client(OllamaClient):
    def chat_stream(self, messages, **kwargs):
        model = self.model
        ai = ollama

        response = ""

        for chunk in ai.chat(model=model, messages=messages, stream=True, **kwargs):
            content = chunk["message"]["content"]
            response += content
            yield content

        messages.append({"role": "assistant", "content": response})
        self.messages = messages

    def chat(
        self,
        prompt: Optional[str] = None,
        messages: Optional[list] = DEFAULT_MESSAGE_HISTORY,
        stream: Optional[bool] = True,
        **kwargs,
    ) -> str:
        model = self.model
        ai = ollama

        if not prompt and not messages:
            raise ValueError("You must pass in a prompt.")

        if messages == DEFAULT_MESSAGE_HISTORY:
            messages = getattr(
                self,
                "messages",
                messages,
            )

        if prompt:
            messages.append({"role": "user", "content": prompt})

        if stream:
            return self.chat_stream(messages, **kwargs)

        chunk = ai.chat(model=model, messages=messages, stream=False, **kwargs)
        response = "".join(chunk["message"]["content"])

        messages.append({"role": "assistant", "content": response})
        self.messages = messages

        return response

    def generate_stream(self, prompt, **kwargs):
        model = self.model
        ai = ollama

        for chunk in ai.generate(model=model, prompt=prompt, stream=True, **kwargs):
            content = chunk["response"]
            yield content

    def generate(self, prompt: str, stream: Optional[bool] = True, **kwargs) -> str:
        model = self.model
        ai = ollama

        if stream:
            return self.generate_stream(prompt)

        chunk = ai.generate(model=model, prompt=prompt, stream=False, **kwargs)
        response = chunk["response"]

        return response

    def clear(self):
        self.messages = [
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
        return model

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


def find_process(command, process_name="ollama"):
    process = None
    for proc in psutil.process_iter(attrs=["cmdline"]):
        try:
            if process_name.lower() in proc.name().lower():
                proc_command = proc.info["cmdline"]
                if proc_command[: len(command)] != command:
                    continue
                process = psutil.Process(pid=proc.pid)
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process


class Cria(Client):
    def __init__(
        self,
        model: Optional[str] = DEFAULT_MODEL,
        standalone: Optional[bool] = False,
        run_subprocess: Optional[bool] = False,
        capture_output: Optional[bool] = False,
        silence_output: Optional[bool] = False,
        close_on_exit: Optional[bool] = True,
    ) -> None:
        self.run_subprocess = run_subprocess
        self.capture_output = capture_output
        self.silence_output = silence_output
        self.close_on_exit = close_on_exit

        ollama_process = find_process(["ollama", "serve"])
        self.ollama_process = ollama_process

        if ollama_process and run_subprocess:
            self.ollama_process.kill()

        try:
            ollama.list()
        except (httpx.ConnectError, httpx.ReadError):
            ollama_process = None

        if not ollama_process:
            ollama_stdout = subprocess.PIPE if capture_output else subprocess.DEVNULL
            ollama_stderr = subprocess.PIPE if capture_output else subprocess.DEVNULL
            try:
                self.ollama_subrprocess = subprocess.Popen(
                    ["ollama", "serve"], stdout=ollama_stdout, stderr=ollama_stderr
                )
            except FileNotFoundError:
                raise FileNotFoundError(
                    "Ollama is not installed, please install ollama from 'https://ollama.com/download'"
                )
            retries = 10
            while retries:
                try:
                    ollama.list()
                    break
                except (httpx.ConnectError, httpx.ReadError):
                    time.sleep(2)
                    retries -= 1
        else:
            self.ollama_subrprocess = None

        self.model = check_models(model, silence_output)

        if not standalone:
            self.llm = find_process(["ollama", "run", self.model])

            if self.llm and run_subprocess:
                self.llm.kill()
                self.llm = subprocess.Popen(
                    ["ollama", "run", self.model],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

        if close_on_exit and self.ollama_subrprocess:
            atexit.register(lambda: self.ollama_subrprocess.kill())

        if close_on_exit and not standalone:
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

        return iter(c for c in iter(lambda: ollama_subprocess.stdout.read(1), b""))

    def close(self):
        llm = self.llm
        llm.kill()


class Model(Cria, ContextDecorator):
    def __init__(
        self,
        model: Optional[str] = DEFAULT_MODEL,
        run_attached: Optional[bool] = False,
        run_subprocess: Optional[bool] = False,
        capture_output: Optional[bool] = False,
        silence_output: Optional[bool] = False,
        close_on_exit: Optional[bool] = True,
    ) -> None:
        super().__init__(
            model=model,
            capture_output=capture_output,
            run_subprocess=False,
            standalone=True,
            close_on_exit=close_on_exit,
        )

        self.capture_output = capture_output
        self.silence_output = silence_output
        self.close_on_exit = close_on_exit

        self.model = check_models(model, silence_output)

        if run_attached and run_subprocess:
            raise ValueError(
                "You cannot run attach to an LLM and run it as a subprocess at the same time."
            )

        if not run_attached:
            llm_stdout = subprocess.PIPE if capture_output else subprocess.DEVNULL
            llm_stderr = subprocess.PIPE if capture_output else subprocess.DEVNULL
            self.llm = subprocess.Popen(
                ["ollama", "run", self.model], stdout=llm_stdout, stderr=llm_stderr
            )
        else:
            self.llm = find_process(["ollama", "run", self.model])

        if self.llm and run_subprocess:
            self.llm.kill()

            llm_stdout = subprocess.PIPE if capture_output else subprocess.DEVNULL
            llm_stderr = subprocess.PIPE if capture_output else subprocess.DEVNULL
            self.llm = subprocess.Popen(
                ["ollama", "run", self.model], stdout=llm_stdout, stderr=llm_stderr
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
