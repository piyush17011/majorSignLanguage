import cv2
import mediapipe as mp
import numpy as np
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Create a folder to store recorded videos
if not os.path.exists("recorded_videos"):
    os.makedirs("recorded_videos")

def storeData(f, data, label):
    with open(f, 'a') as fo:
        fo.write(f"{data}, {label}\n")

@app.route('/start-recording', methods=['POST'])
def start_recording():
    gesture_name = request.json.get("gesture_name", "Unknown")  # Get label from request
    filename = f"recorded_videos/{gesture_name}.avi"  # Store video with label name

    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # Convert image format
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Extract hand landmark data
                    data = [f"{lm.x},{lm.y},{lm.z}" for lm in hand_landmarks.landmark]
                    storeData('Gesture.csv', ",".join(data), gesture_name)

            out.write(image)  # Save video frame
            cv2.imshow('Recording Sign', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to stop recording
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return jsonify({"message": f"Recording saved as {filename}"})

if __name__ == '__main__':
    app.run(debug=True)
