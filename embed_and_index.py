import os
import openai
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from tqdm import tqdm

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TXT_DIR = '.'  # base folder to scan .txt files from

chroma_client = Client(Settings(persist_directory="./chroma_store"))
embedding_func = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY)

collection = chroma_client.get_or_create_collection(name="bahthgpt", embedding_function=embedding_func)

def smart_chunk(text, max_chars=1000):
    chunks = []
    current = ""
    for line in text.splitlines():
        if not line.strip():
            continue
        if len(current) + len(line) < max_chars:
            current += line.strip() + " "
        else:
            chunks.append(current.strip())
            current = line.strip() + " "
    if current:
        chunks.append(current.strip())
    return chunks

def embed_all_files():
    docs = []
    metadatas = []
    ids = []

    for root, dirs, files in os.walk(TXT_DIR):
        for fname in files:
            if fname.endswith('.txt'):
                path = os.path.join(root, fname)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        chunks = smart_chunk(text)
                        for i, chunk in enumerate(chunks):
                            docs.append(chunk)
                            metadatas.append({
                                "file": path.replace('./', ''),
                                "chunk": i
                            })
                            ids.append(f"{path}-{i}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

    print(f"Embedding {len(docs)} chunks...")
    collection.add(documents=docs, metadatas=metadatas, ids=ids)
    print("Indexing complete.")

if __name__ == '__main__':
    embed_all_files()
