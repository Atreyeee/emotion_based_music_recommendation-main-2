from django.test import TestCase

# Create your tests here.
import cv2
import mediapipe as mp
import screen_brightness_control as sbc  # Import brightness control library

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

# Start video capture (0 is the default camera)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the image to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame for hand landmarks
    results = hands.process(rgb_frame)

    # If hands are detected, draw landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Example logic for gesture recognition (hand position)
            wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y
            if wrist_y > 0.5:  # Hand is up
                cv2.putText(frame, "Hand Up (Volume Up)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Increase brightness
                try:
                    current_brightness = sbc.get_brightness()
                    new_brightness = min(current_brightness[0] + 10, 100)  # Increase by 10%, max 100%
                    sbc.set_brightness(new_brightness)
                    print(f"Brightness increased to {new_brightness}%")
                except Exception as e:
                    print(f"Error increasing brightness: {e}")

            else:  # Hand is down
                cv2.putText(frame, "Hand Down (Volume Down)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Decrease brightness
                try:
                    current_brightness = sbc.get_brightness()
                    new_brightness = max(current_brightness[0] - 10, 0)  # Decrease by 10%, min 0%
                    sbc.set_brightness(new_brightness)
                    print(f"Brightness decreased to {new_brightness}%")
                except Exception as e:
                    print(f"Error decreasing brightness: {e}")

    # Display the frame with the landmarks and gesture message
    cv2.imshow('Gesture Recognition', frame)

    # Press 'q' to quit the webcam window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close the window
cap.release()
cv2.destroyAllWindows()
