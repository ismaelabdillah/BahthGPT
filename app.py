import os
from flask import Flask, request, jsonify

app = Flask(__name__)
TEXT_DIR = './texts'

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '').lower()
    matches = []

    if not os.path.exists(TEXT_DIR):
        return jsonify({"error": "Text directory not found."}), 500

    for fname in os.listdir(TEXT_DIR):
        if fname.endswith('.txt'):
            with open(os.path.join(TEXT_DIR, fname), 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if query in line.lower():
                        matches.append({
                            'file': fname,
                            'line_number': i,
                            'text': line.strip()
                        })
    return jsonify(matches)
