import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def storeData(f, a):
    with open(f, 'a') as fo:
        fo.write(str(a))

# For static images:
IMAGE_FILES = []  # Add paths to your images here

with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,  # Allow up to 2 hands
    min_detection_confidence=0.5) as hands:
    for idx, file in enumerate(IMAGE_FILES):
        # Read an image, flip it around y-axis for correct handedness output
        image = cv2.flip(cv2.imread(file), 1)
        # Convert the BGR image to RGB before processing
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Print handedness and draw hand landmarks on the image
        print('Handedness:', results.multi_handedness)
        if not results.multi_hand_landmarks:
            continue
        image_height, image_width, _ = image.shape
        annotated_image = image.copy()
        for hand_landmarks in results.multi_hand_landmarks:
            print('hand_landmarks:', hand_landmarks)
            print(
                f'Index finger tip coordinates: (',
                f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
                f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
            )
            mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
        cv2.imwrite(
            '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))

        # Draw hand world landmarks
        if not results.multi_hand_world_landmarks:
            continue
        for hand_world_landmarks in results.multi_hand_world_landmarks:
            mp_drawing.plot_landmarks(
                hand_world_landmarks, mp_hands.HAND_CONNECTIONS, azimuth=5)

# For webcam input:
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=2) as hands:  # Allow detection of up to 2 hands
    while cap.isOpened():
        success, image = cap.read()
        imageWidth, imageHeight = image.shape[:2]
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # To improve performance, optionally mark the image as not writeable
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                # Process the landmarks data
                data = []
                for point in mp_hands.HandLandmark:
                    normalizedLandmark = hand_landmarks.landmark[point]
                    pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(
                        normalizedLandmark.x, normalizedLandmark.y, imageWidth, imageHeight)

                    data.append(normalizedLandmark.x)
                    data.append(normalizedLandmark.y)
                    data.append(normalizedLandmark.z)

                # Save the data
                data = str(data)
                data = data[1:-1]
                image = cv2.flip(image, 1)
                storeData('Gesture.csv', data + ', Salute\n')
                

        # Flip the image horizontally for a selfie-view display
        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):  # Exit on pressing 'q'
            break

cap.release()
cv2.destroyAllWindows()
