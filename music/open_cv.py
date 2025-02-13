# import cv2
# from deepface import DeepFace
# import numpy as np
# import base64
# from io import BytesIO
# from PIL import Image

# def detect_emotion(frame_base64):
#     # Decode the base64 frame
#     frame_data = base64.b64decode(frame_base64.split(",")[1])
#     frame = np.array(Image.open(BytesIO(frame_data)))

#     # Perform emotion detection
#     try:
#         result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
#         emotion = result[0]["dominant_emotion"]
#     except Exception:
#         emotion = "Error"

#     return emotion
