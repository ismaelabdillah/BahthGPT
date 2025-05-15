@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json.get('query', '').strip()
        line_offset = int(request.json.get('line_offset', 0))
        line_limit = int(request.json.get('line_limit', 1000))
        target_file = request.json.get('filename', '').strip()
        if not query:
            return jsonify({"error": "Empty query"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid request: " + str(e)}), 400

    matches = []

    for root, dirs, files in os.walk('.'):
        for fname in files:
            if fname.endswith('.txt'):
                if target_file and target_file != fname:
                    continue  # skip files that aren't the target
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if i < line_offset:
                                continue
                            if i >= line_offset + line_limit:
                                break
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

    return jsonify({
        "filename": target_file if target_file else None,
        "line_offset": line_offset,
        "line_limit": line_limit,
        "results_found": len(matches),
        "results": matches
    })
