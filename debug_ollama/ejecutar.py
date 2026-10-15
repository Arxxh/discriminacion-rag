"""Ejecutar el app.py original con un proveedor local solo en este proceso."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import time
import urllib.error
import urllib.request

from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableLambda
import langchain_google_genai as genai

ORIGINAL_SHA256 = "835e55c3eb2179b207e7319dd48b06e1f3baa45f00a58eb5f0dfa4e97195c96e"
API = "http://127.0.0.1:11434"


def request(endpoint, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API + endpoint, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama devolvió HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError("No se pudo conectar con Ollama. Abre Ollama y reintenta.") from error


class LocalEmbeddings(Embeddings):
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        if not texts:
            return []
        result = request("/api/embed", {"model": self.model, "input": texts,
                                       "truncate": False, "keep_alive": "0"})
        vectors = result.get("embeddings", [])
        if len(vectors) != len(texts) or any(not vector for vector in vectors):
            raise RuntimeError("Ollama no devolvió todos los embeddings solicitados.")
        return vectors

    def embed_query(self, text):
        return self.embed_documents([text])[0]


def local_chat(model, temperature):
    def respond(prompt):
        roles = {"human": "user", "ai": "assistant", "system": "system"}
        messages = [{"role": roles[message.type], "content": message.content}
                    for message in prompt.to_messages()]
        result = request("/api/chat", {"model": model, "messages": messages,
                         "stream": False, "keep_alive": "0",
                         "options": {"temperature": temperature, "num_ctx": 8192}})
        text = result.get("message", {}).get("content")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Ollama devolvió una respuesta vacía.")
        return text
    return RunnableLambda(respond)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--chat-model", default="qwen3:4b-instruct")
    parser.add_argument("--embedding-model", default="embeddinggemma:300m")
    args = parser.parse_args()
    project = args.project.resolve()
    app = project / "app.py"
    if not app.is_file() or digest(app) != ORIGINAL_SHA256:
        raise RuntimeError("app.py no coincide con el original de Base.rar. No se ejecutó.")
    pdfs = sorted((project / "conocimientos").rglob("*.pdf"))
    if not pdfs:
        raise RuntimeError("No hay PDF dentro de conocimientos/.")
    installed = {model["name"] for model in request("/api/tags").get("models", [])}
    missing = {args.chat_model, args.embedding_model} - installed
    if missing:
        raise RuntimeError("Faltan modelos locales: " + ", ".join(sorted(missing)))

    runtime = project / "debug_ollama" / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    knowledge = runtime / "conocimientos"
    if not knowledge.exists():
        knowledge.symlink_to(project / "conocimientos", target_is_directory=True)
    if knowledge.resolve() != (project / "conocimientos").resolve():
        raise RuntimeError("La carpeta de depuración apunta a otro corpus.")
    state = {"app_sha256": ORIGINAL_SHA256, "embedding_model": args.embedding_model,
             "pdf_sha256": {str(pdf.relative_to(project)): digest(pdf) for pdf in pdfs}}
    manifest = runtime / "manifest.json"
    index = runtime / "faiss_index"
    previous = json.loads(manifest.read_text()) if manifest.exists() else None
    index_files = [index / "index.faiss", index / "index.pkl"]
    trusted = (previous is not None and previous.get("source") == state
               and all(path.is_file() for path in index_files)
               and previous.get("index_sha256") == {path.name: digest(path) for path in index_files})
    if index.exists() and not trusted:
        backups = runtime / "respaldos"
        backups.mkdir(exist_ok=True)
        shutil.move(str(index), str(backups / ("faiss_index_" + str(time.time_ns()))))

    original_embeddings = genai.GoogleGenerativeAIEmbeddings
    original_chat = genai.ChatGoogleGenerativeAI
    genai.GoogleGenerativeAIEmbeddings = lambda **kwargs: LocalEmbeddings(args.embedding_model)
    genai.ChatGoogleGenerativeAI = lambda **kwargs: local_chat(args.chat_model, kwargs["temperature"])
    initial_directory = Path.cwd()
    print("PRUEBA LOCAL: se ejecuta el app.py original con Ollama, sin editarlo.")
    print(f"Respuesta: {args.chat_model}; embeddings: {args.embedding_model}.")
    print(f"Índice de prueba: {index}")
    try:
        os.chdir(runtime)
        runpy.run_path(str(app), run_name="__main__")
        if all(path.is_file() for path in index_files):
            manifest.write_text(json.dumps({"source": state,
                "index_sha256": {path.name: digest(path) for path in index_files}}, indent=2))
    finally:
        os.chdir(initial_directory)
        genai.GoogleGenerativeAIEmbeddings = original_embeddings
        genai.ChatGoogleGenerativeAI = original_chat
        if digest(app) != ORIGINAL_SHA256:
            raise RuntimeError("app.py cambió durante la prueba.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyboardInterrupt, EOFError) as error:
        print(f"Prueba detenida: {error}", file=sys.stderr)
        sys.exit(1)
