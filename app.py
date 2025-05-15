from flask import Flask, request, jsonify
import os
import difflib

app = Flask(__name__)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def is_fuzzy_match(query, line, threshold=0.7):
    return difflib.SequenceMatcher(None, query, line).ratio() >= threshold

@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json.get('query', '').strip()
        offset = int(request.json.get('offset', 0))
        limit = int(request.json.get('limit', 100))
        if not query:
            return jsonify({"error": "Empty query"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid request: " + str(e)}), 400

    all_matches = []

    for root, dirs, files in os.walk('.'):
        for fname in files:
            if fname.endswith('.txt'):
                fpath = os.path.join(root, fname)
                if os.path.getsize(fpath) > MAX_FILE_SIZE:
                    continue
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if is_fuzzy_match(query, line.strip()):
                                all_matches.append({
                                    'file': fpath.replace('./', ''),
                                    'line_number': i,
                                    'text': line.strip()
                                })
                except Exception as e:
                    all_matches.append({
                        'file': fpath.replace('./', ''),
                        'error': f"Failed to read: {str(e)}"
                    })

    # Apply pagination
    paginated = all_matches[offset:offset+limit]
    return jsonify({
        "total_matches": len(all_matches),
        "returned": len(paginated),
        "offset": offset,
        "limit": limit,
        "results": paginated
    })
