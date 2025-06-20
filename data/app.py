import os
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import io
from PIL import Image
from flask_cors import CORS  # To handle CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define class names corresponding to model's output indices
class_names = ['Chickenpox', 'Cowpox', 'Healthy', 'HFMD', 'Measles', 'Monkeypox']

# Load your pre-trained Keras model
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Models', 'best_overall_model.h5')

try:
    model = load_model(MODEL_PATH)
    model.make_predict_function()  # Necessary for some TensorFlow versions
    print('Model loaded successfully.')
except Exception as e:
    print(f'Error loading model: {e}')

# Define the expected image size (adjust based on your model's input)
IMG_HEIGHT, IMG_WIDTH = 224, 224

def preprocess_image(img):
    img = img.resize((IMG_WIDTH, IMG_HEIGHT))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize if your model expects normalized input
    return img_array

def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        img = Image.open(io.BytesIO(file.read())).convert('RGB')
        processed_img = preprocess_image(img)
        prediction = model.predict(processed_img)
        predicted_class_idx = np.argmax(prediction, axis=1)[0]
        confidence = float(prediction.max(axis=1)[0])  # Convert to native float

        # Map the predicted index to the class label
        predicted_class_label = class_names[predicted_class_idx]

        return jsonify({
            'prediction': predicted_class_label,
            'confidence': round(confidence, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def handle_predict():
    return predict()

if __name__ == '__main__':
    app.run(debug=True)