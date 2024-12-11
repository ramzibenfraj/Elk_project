from flask import Flask, request, render_template, jsonify, redirect, url_for  # Add the imports here
import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

app = Flask(__name__)
UPLOAD_FOLDER = '/app/data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

es = Elasticsearch(['http://elasticsearch:9200'])
INDEX_NAME = "csv_data"

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Log successful file upload
            app.logger.debug(f"File {file.filename} saved successfully at {file_path}")

            # Redirect to dashboard after upload
            return render_template('upload.html')

    except Exception as e:
        app.logger.error(f"Error during file upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    app.logger.debug("Rendering dashboard page")
    return render_template('dashboard.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query', '')
        try:
            # Elasticsearch query
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["Category", "Product_ID", "Payment_Method"]
                    }
                }
            }
            
            # Execute search
            response = es.search(index=INDEX_NAME, body=search_body)
            hits = response['hits']['hits']
            return render_template('search.html', query=query, results=hits)
            
        except ConnectionError:
            return render_template('search.html', query=query, results=[], error="Could not connect to Elasticsearch")
        except Exception as e:
            return render_template('search.html', query=query, results=[], error=str(e))
            
    return render_template('search.html', query='', results=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
