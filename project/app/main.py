from flask import Flask, request, render_template, jsonify
import os

import requests 

app = Flask(__name__)
UPLOAD_FOLDER = '/app/data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ELASTICSEARCH_URL = "http://elasticsearch:9200"
INDEX_NAME = "ecommerce_data"

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query', '')
        # Perform search in Elasticsearch
        search_url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search"
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["Category", "Product_ID", "Payment_Method"]  # Adjust based on indexed fields
                }
            }
        }
        response = requests.post(search_url, json=search_query)
        results = response.json()
        hits = results.get('hits', {}).get('hits', [])
        return render_template('search.html', query=query, results=hits)
    return render_template('search.html', query='', results=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
