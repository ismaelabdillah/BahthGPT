from flask import Flask, request, jsonify
import os
import difflib

app = Flask(__name__)

def is_fuzzy_match(query, line, threshold=0.7):
    ratio = difflib.SequenceMatcher(None, query, line).ratio()
    return ratio >= threshold

@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json.get('query', '').strip()
        if not query:
            return jsonify({"error": "Empty query"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid request: " + str(e)}), 400

    matches = []

    for root, dirs, files in os.walk('.'):
        for fname in files:
            if fname.endswith('.txt'):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if is_fuzzy_match(query, line.strip()):
                                matches.append({
                                    'file': fpath.replace('./', ''),
                                    'line_number': i,
                                    'text': line.strip()
                                })
                except Exception as e:
                    matches.append({
                        'file': fpath.replace('./', ''),
                        'error': f"Failed to read: {str(e)}"
                    })

    return jsonify(matches)
