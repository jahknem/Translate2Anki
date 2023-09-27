from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # To handle CORS issues when calling from frontend
from PIL import Image
import pytesseract
import io
import openai
import base64
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        logging.debug(f'Starting process_image')
        if request.is_json:
            logging.debug(f'Request is JSON')
            image_data = request.json.get('image')
            if not image_data:
                logging.error('No image received in JSON')
                return jsonify({'error': 'No image received in JSON'}), 400
            image_data = base64.b64decode(image_data)
        else:
            logging.debug(f'Request is FormData')
            image_file = request.files.get('image')
            if not image_file:
                logging.error('No image received in FormData')
                return jsonify({'error': 'No image received in FormData'}), 400
            image_data = image_file.read()

        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        logging.debug(f'image_data length: {len(image_data)}')
        logging.debug(f'image format: {image.format}')

        # OCR with pytesseract
        ocr_text = pytesseract.image_to_string(image)
        logging.debug(f'ocr_text: {ocr_text}')

        messages = [
            {"role": "user", "content": f"Translate the following text to English: {ocr_text}"}
        ]

        # Use OpenAI's chat-based API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100
        )

        # Extract translated text
        translated_text = response['choices'][0]['message']['content'].strip()


        return jsonify({
            'ocr_text': ocr_text,
            'translated_text': translated_text,
            'backend_log': f"OCR Text: {ocr_text}, Translated Text: {translated_text}"
        })
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
