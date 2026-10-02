import base64
import json
import logging

import cv2
import mediapipe as mp
import numpy as np
from deepface import DeepFace
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import angry, fear, happy, neutral, sad, surprise
from .serializer import (
    AngrySongSerializer,
    FearSongSerializer,
    HappySongSerializer,
    NeutralSongSerializer,
    SadSongSerializer,
    SurpriseSongSerializer,
)

logger = logging.getLogger(__name__)

# Single source of truth mapping a mood name to its model/serializer/template.
# Every mood-specific view and URL used to be copy-pasted six times (and the
# six API endpoints even collided on the same URL, permanently hiding five
# of them) — this dict is what replaces all of that duplication.
MOOD_REGISTRY = {
    "neutral": {"model": neutral, "serializer": NeutralSongSerializer, "label": "Neutral"},
    "happy": {"model": happy, "serializer": HappySongSerializer, "label": "Happy"},
    "sad": {"model": sad, "serializer": SadSongSerializer, "label": "Sad"},
    "fear": {"model": fear, "serializer": FearSongSerializer, "label": "Fear"},
    "surprise": {"model": surprise, "serializer": SurpriseSongSerializer, "label": "Surprise"},
    "angry": {"model": angry, "serializer": AngrySongSerializer, "label": "Angry"},
}

mp_face_detection = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)


def index(request):
    if request.user.is_authenticated:
        return redirect("webcam")
    return render(request, "index.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user_auth = authenticate(request, username=username, password=password)
        if user_auth is not None:
            auth_login(request, user_auth)
            return redirect("webcam")

        messages.error(request, "Invalid username or password.")
        return redirect("login")

    return render(request, "login.html")


def signup(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if len(username) < 3:
            messages.error(request, "Username must be at least 3 characters.")
            return redirect("signup")
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return redirect("signup")
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("signup")
        if User.objects.filter(username=username).exists():
            messages.error(request, "That username is taken.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        user_login = authenticate(request, username=username, password=password)
        if user_login is not None:
            auth_login(request, user_login)
            return redirect("webcam")

        messages.info(request, "Account created — please log in.")
        return redirect("login")

    return render(request, "signup.html")


@login_required(login_url="login")
def logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required(login_url="login")
def webcam_page(request):
    return render(request, "web_cam.html", {"username": request.user.username, "moods": MOOD_REGISTRY})


@login_required(login_url="login")
def playlist(request, mood):
    entry = MOOD_REGISTRY.get(mood)
    if entry is None:
        messages.error(request, "Unknown mood.")
        return redirect("webcam")

    songs = entry["model"].objects.all()
    return render(
        request,
        "playlist.html",
        {"songs": songs, "mood": mood, "mood_label": entry["label"], "moods": MOOD_REGISTRY},
    )


def process_frame(frame):
    """Detects the primary face in a frame and classifies its emotion.
    Returns (frame, emotion_label, face_box_dict_or_None).
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_face_detection.process(rgb_frame)

    detected_emotion = None
    face_box = None

    if results.detections:
        # Use the highest-confidence detection rather than looping over
        # every face found — keeps results meaningful when bystanders are
        # in frame, and matches how a single-user webcam flow should behave.
        best = max(results.detections, key=lambda d: d.score[0])
        bboxC = best.location_data.relative_bounding_box
        h, w, _ = frame.shape
        x = max(0, int(bboxC.xmin * w))
        y = max(0, int(bboxC.ymin * h))
        width = min(w - x, int(bboxC.width * w))
        height = min(h - y, int(bboxC.height * h))
        face_box = {"x": x, "y": y, "width": width, "height": height}

        face_roi = frame[y : y + height, x : x + width]
        if face_roi.size > 0:
            try:
                analysis = DeepFace.analyze(face_roi, actions=["emotion"], enforce_detection=False)
                detected_emotion = analysis[0]["dominant_emotion"]
            except Exception as exc:  # noqa: BLE001
                logger.warning("Emotion analysis failed")

    return frame, detected_emotion, face_box


@csrf_exempt
@require_POST
def detect_emotion(request):
    """Accepts a single base64-encoded frame (from the browser's webcam or
    an uploaded image) and returns the detected emotion and face box.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    frame_data = data.get("frame")
    if not frame_data:
        return JsonResponse({"error": "No frame data provided"}, status=400)

    try:
        encoded = frame_data.split(",")[1] if frame_data.startswith("data:image") else frame_data
        decoded = base64.b64decode(encoded)
        np_data = np.frombuffer(decoded, np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
    except Exception:
        return JsonResponse({"error": "Failed to decode frame"}, status=400)

    if frame is None:
        return JsonResponse({"error": "Failed to decode frame"}, status=400)

    _, detected_emotion, face_box = process_frame(frame)

    playlist_url = None
    if detected_emotion and detected_emotion in settings.MOOD_PLAYLIST_MAP:
        from django.urls import reverse

        playlist_url = reverse("playlist", args=[settings.MOOD_PLAYLIST_MAP[detected_emotion]])

    return JsonResponse({"emotion": detected_emotion, "face_box": face_box, "playlist_url": playlist_url})


class MoodSongListView(APIView):
    """Single parametrized API view replacing the six mood-specific
    APIViews that previously all fought over the same `/api/songs/` URL.
    """

    def get(self, request, mood):
        entry = MOOD_REGISTRY.get(mood)
        if entry is None:
            return Response({"error": f"Unknown mood '{mood}'"}, status=404)

        songs = entry["model"].objects.all()
        serializer = entry["serializer"](songs, many=True, context={"request": request})
        return Response(serializer.data)
