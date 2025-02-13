from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from requests import post
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.http import StreamingHttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
# from .open_cv import detect_emotion
from .models import *
from .serializer import *
import cv2
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
import mediapipe as mp
from deepface import DeepFace
import base64
import numpy as np
import cv2
import mediapipe as mp
import pyautogui
import screen_brightness_control as sbc



# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.3)


# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5,min_tracking_confidence=0.5 )



def neutral_playlist(request):
    neutral_songs=neutral.objects.all()
    return render(request,'neutral_playlist.html',{'neutral_playlist':neutral_songs})

class NeutralSongListView(APIView):
    def get(self, request):
        songs = neutral.objects.all()  # Fetch all songs from the database
        serializer = NeutralSongSerializer(songs, many=True)  # Serialize the list of songs
        return Response(serializer.data)
    
def happy_playlist(request):
    happy_songs=happy.objects.all()
    return render(request,'happy_playlist.html',{'happy_playlist':happy_songs})

class HappySongListView(APIView):
    def get(self, request):
        songs = happy.objects.all()  # Fetch all songs from the database
        serializer = HappySongSerializer(songs, many=True)  # Serialize the list of songs
        return Response(serializer.data)
    
def fear_playlist(request):
    fear_songs=fear.objects.all()
    return render(request,'fear_playlist.html',{'fear_playlist':fear_songs})

class FearSongListView(APIView):
    def get(self, request):
        songs = fear.objects.all()  # Fetch all songs from the database
        serializer = FearSongSerializer(songs, many=True)  # Serialize the list of songs
        return Response(serializer.data)

def sad_playlist(request):
    sad_songs=sad.objects.all()
    return render(request,'sad_playlist.html',{'sad_playlist':sad_songs})

class SadSongListView(APIView):
    def get(self, request):
        songs = sad.objects.all()  # Fetch all songs from the database
        serializer = SadSongSerializer(songs, many=True)  # Serialize the list of songs
        return Response(serializer.data)
    
def angry_playlist(request):
    angry_songs=angry.objects.all()
    return render(request,'angry_playlist.html',{'angry_playlist':angry_songs})

class AngrySongListView(APIView):
    def get(self, request):
        songs = angry.objects.all()  # Fetch all songs from the database
        serializer = AngrySongSerializer(songs, many=True)  # Serialize the list of songs
        return Response(serializer.data)
    
def surprise_playlist(request):
    surprise_songs=surprise.objects.all()
    return render(request,'surprise_playlist.html',{'surprise_playlist':surprise_songs})

class SurpriseSongListView(APIView):
    def get(self, request):
        songs = surprise.objects.all()  # Fetch all songs from the database
        serializer = SurpriseSongSerializer(songs, many=True)  # Serialize the list of songs
        return Response(serializer.data)

def index(request):
    return render(request,'index.html')

def login(request):
    if request.method == 'POST':  # Check if the request is POST
        username = request.POST['username']
        password = request.POST['password']
    
        user_auth = auth.authenticate(username=username, password=password)
        
        if user_auth is not None:  # Check if authentication is successful
            print(f"User authenticated: {request.user.is_authenticated}")
            # Log the user in
            auth_login(request, user_auth)  # Using the renamed login function
            return redirect('webcam')  # Redirect to webcam page if authenticated
        else:
            messages.info(request, 'Invalid credentials')  # Invalid login attempt
            return redirect('login')  # Redirect to login page if authentication fails

    else:
        return render(request, 'login.html')  # Render the ligin page if request is GET
    
def signup(request):
     if request.method == 'POST':  # Check if the request is POST
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password1']
        password2 = request.POST['password2']

        if password == password2:  # Check if passwords match
            if User.objects.filter(email=email).exists():  # Check if email is already registered
                messages.info(request, 'Email is already registered')
                return redirect('login')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken ')
                return redirect('login')
            else:
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password
                )
                user.save()

                # Log the user in after sign-up
                user_login = auth.authenticate(username=username, password=password)
                if user_login is not None:
                    auth.login(request, user_login)
                    return redirect('webcam')  # Redirect to the home or webcam page
                else:
                    messages.info(request, 'Error logging in after sign-up')
                    return redirect('login')

        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
     else: 
        return render(request, 'signup.html')
    
@login_required(login_url='login')
def webcam_page(request):
    # Pass the logged-in user's first name to the template
    username = request.user.username
    return render(request, 'web_cam.html', {'username': username})

def logout(request):
    pass

def video_stream(request):
    return StreamingHttpResponse(generate(), content_type="multipart/x-mixed-replace; boundary=frame")

# Generate Frames with Emotion Detection
def generate():
    try:
        # Initialize the webcam
        cam = cv2.VideoCapture(0)
        while True:
            ret, frame = cam.read()
            if not ret:
                break

            # Detect emotion and draw on the frame
            try:
                frame, emotion,face_box = process_frame(frame)
            except Exception as e:
                print(f"Error during emotion detection: {e}")
                cv2.putText(frame, "Error detecting emotion", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # Detect and draw hand gestures
            try:
                frame = recognize_gesture(frame)  # Hand gesture recognition
            except Exception as e:
                print(f"Error detecting gestures: {e}")
            # Encode the frame as JPEG
            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()

            # Yield the frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    except Exception as e:
        print(f"Error in generate(): {e}")
    finally:
        cam.release()

# Process Frame for Emotion Detection
def process_frame(frame):
    # Convert to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run MediaPipe Face Detection
    results = mp_face_detection.process(rgb_frame)

    detected_emotion = "neutral"  # Default emotion
    face_box = None  # Default face box

    if results.detections:
        for detection in results.detections:
            # Get bounding box coordinates
            bboxC = detection.location_data.relative_bounding_box
            h, w, _ = frame.shape
            x, y, width, height = (
                int(bboxC.xmin * w),
                int(bboxC.ymin * h),
                int(bboxC.width * w),
                int(bboxC.height * h),
            )

            # Draw a green bounding box around the face
            cv2.rectangle(rgb_frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

            # Save face box coordinates to return
            face_box = {"x": x, "y": y, "width": width, "height": height}

            # Extract the region of interest (ROI) for emotion detection
            face_roi = rgb_frame[y:y + height, x:x + width]

            # Use DeepFace to detect emotion
            try:
                analysis = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                detected_emotion = analysis[0]['dominant_emotion']  # Get the dominant emotion
                print(f"Detected Emotion: {detected_emotion}")
            except Exception as e:
                print(f"Error in emotion detection: {e}")

            # Define coordinates for the label box
            label_width = max(100, width // 3)  # Adjust the width of the label box
            label_x2 = x + label_width
            label_y2 = max(0, y - 10)  # Ensure it doesn't go out of bounds

            # Draw the white box for the label
            cv2.rectangle(rgb_frame, (x, label_y2 - 30), (label_x2, label_y2), (255, 255, 255), -1)

            # Overlay the emotion label text inside the white box
            cv2.putText(
                rgb_frame,
                detected_emotion.capitalize(),  # Capitalize the emotion label
                (x + 5, label_y2 - 10),  # Adjust text position for visibility
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,  # Font size
                (0, 0, 0),  # Text color (black)
                2,  # Thickness
            )


    return frame, detected_emotion, face_box # Return both emotion and face_box

 
# Emotion Detection API
@csrf_exempt
def detect_emotion(request):
    if request.method == "POST":
        try:
            # Parse and decode the frame data
            data = json.loads(request.body.decode("utf-8"))
            frame_data = data.get("frame")
            if not frame_data:
                return JsonResponse({"error": "No frame data provided"}, status=400)

            # Decode base64 image data
            encoded_data = frame_data.split(",")[1] if frame_data.startswith('data:image') else frame_data
            decoded_data = base64.b64decode(encoded_data)
            np_data = np.frombuffer(decoded_data, np.uint8)
            frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({"error": "Failed to decode frame"}, status=400)

            # Process the frame for emotion detection
            frame, detected_emotion, face_box = process_frame(frame)
            frame = recognize_gesture(frame)

            # Include the emotion and face box in the response
            return JsonResponse({"emotion": detected_emotion, "face_box": face_box})

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


# Image Upload API
@csrf_exempt
def upload_image(request):
    if request.method == "POST":
        try:
            # Get the uploaded image
            uploaded_file = request.FILES.get("image")
            if not uploaded_file:
                return JsonResponse({"error": "No image provided"}, status=400)

            # Read the uploaded image
            file_bytes = uploaded_file.read()
            np_data = np.frombuffer(file_bytes, np.uint8)
            frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({"error": "Failed to decode image"}, status=400)

            # Process the frame for emotion detection
            _, detected_emotion = process_frame(frame)

            return JsonResponse({"emotion": detected_emotion})

        except Exception as e:
            print(f"Error processing uploaded image: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# Function to increase brightness
def increase_brightness():
    try:
        current_brightness = sbc.get_brightness()
        new_brightness = min(current_brightness[0] + 10, 100)  # Increase by 10%, max 100%
        sbc.set_brightness(new_brightness)
        print(f"Brightness increased to {new_brightness}%")
    except Exception as e:
        print(f"Error increasing brightness: {e}")

# Function to decrease brightness
def decrease_brightness():
    try:
        current_brightness = sbc.get_brightness()
        new_brightness = max(current_brightness[0] - 10, 0)  # Decrease by 10%, min 0%
        sbc.set_brightness(new_brightness)
        print(f"Brightness decreased to {new_brightness}%")
    except Exception as e:
        print(f"Error decreasing brightness: {e}")

# Function to increase volume
def increase_volume():
    pyautogui.press("volumeup")  # Press volume up key
    print("Volume Up")

# Function to decrease volume
def decrease_volume():
    pyautogui.press("volumedown")  # Press volume down key
    print("Volume Down")

# Recognize gestures in real-time
def recognize_gesture(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Hand gesture detection
    hand_results = hands.process(rgb_frame)
    if hand_results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
            hand_type = handedness.classification[0].label
            wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y

            if wrist_y > 0.5:  # Hand is up
                if hand_type == "Left":
                    increase_volume()  # Left hand up: Volume Up
                elif hand_type == "Right":
                    increase_brightness()  # Right hand up: Brightness Up
            else:  # Hand is down
                if hand_type == "Left":
                    decrease_volume()  # Left hand down: Volume Down
                elif hand_type == "Right":
                    decrease_brightness()  # Right hand down: Brightness Down

            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Optionally, draw each hand landmark as a small circle (you can customize this part)
            for landmark in hand_landmarks.landmark:
                # Convert normalized coordinates to pixel values
                h, w, _ = frame.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)  # Draw green circle on each landmark

    return frame


