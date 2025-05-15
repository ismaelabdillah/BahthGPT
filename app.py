from flask import Flask, request, jsonify
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os

app = Flask(__name__)

embedding_func = embedding_functions.OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = Client(Settings(persist_directory="./chroma_store"))
collection = chroma_client.get_or_create_collection(name="bahthgpt", embedding_function=embedding_func)

@app.route("/")
def home():
    return "BahthGPT vector search is live."

@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.json["question"]
    except Exception:
        return jsonify({"error": "Missing 'question' in request"}), 400

    results = collection.query(query_texts=[question], n_results=5)

    output = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        output.append({
            "file": meta["file"],
            "chunk": meta["chunk"],
            "text": doc
        })

    return jsonify({
        "question": question,
        "results": output
    })
