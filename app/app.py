import os
from flask import Flask, jsonify, request
from app.extract_data import ImageProcessor


app = Flask(__name__)


@app.route('/health')
def hello_world():
    return 'Alive!'


@app.route('/extract-data', methods=['POST'])
def extract_data_endpoint():
    data = request.json
    url = data.get('url', None)

    if not url:
        return jsonify({"error": "URL not provided"}), 400

    processor = ImageProcessor(url)
    username = processor.get_username()
    match_info = processor.get_match_info()

    data = {'username': username, 'match_info': match_info}

    os.remove("tmp.jpg")

    return jsonify(data)


if __name__ == '__main__':
    try:
        app.run(port=os.environ.get('PORT', 5000))
    except Exception as e:
        print("Error starting server", e)
