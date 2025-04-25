from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import cv2
import mediapipe as mp
import pickle

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the trained model
model_path = r'C:\Users\piyus\Desktop\RealTimeWorkingMain\models\model.pkl'
try:
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500  # Return error if model is missing

    try:
        if 'frame' not in request.form:
            return jsonify({'error': 'No frame in request'}), 400

        image_data = request.form['frame']
        if not image_data:
            return jsonify({'error': 'Received empty image data'}), 400

        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Convert to RGB for MediaPipe processing
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process hand landmarks
        with mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.5) as hands:
            results = hands.process(img_rgb)

            if not results.multi_hand_landmarks:
                return jsonify({'prediction': ''})   #no hands

            data = []
            for hand_landmarks in results.multi_hand_landmarks:
                for point in mp_hands.HandLandmark:
                    landmark = hand_landmarks.landmark[point]
                    data.extend([landmark.x, landmark.y, landmark.z])  # Collect landmark data

            if len(data) != model.n_features_in_:  # Ensure correct feature size
                return jsonify({'error': 'Incorrect input size for model'})

            # Make a prediction
            prediction = model.predict([data])[0]

            return jsonify({'prediction': prediction})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
