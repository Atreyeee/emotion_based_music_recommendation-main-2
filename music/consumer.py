# import json
# from channels.generic.websocket import WebsocketConsumer
# from .open_cv import detect_emotion
# import base64
# import numpy as np
# import cv2

# class EmotionDetectionConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#         self.send(text_data=json.dumps({
#             'message': 'WebSocket connected'
#         }))

#     def disconnect(self, close_code):
#         pass

#     def receive(self, text_data):
#         data = json.loads(text_data)
#         frame_base64 = data.get('frame')

#         if frame_base64:
#             # Decode the incoming frame
#             frame_data = base64.b64decode(frame_base64.split(",")[1])
#             np_arr = np.frombuffer(frame_data, np.uint8)
#             frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#             # Use the logic from open_cv.py
#             emotion = detect_emotion(frame_base64)

#             # Encode the processed frame back to send to the client
#             _, buffer = cv2.imencode('.jpg', frame)
#             processed_frame_base64 = base64.b64encode(buffer).decode('utf-8')

#             # Send the processed frame and emotion back to the client
#             self.send(text_data=json.dumps({
#                 'frame': f'data:image/jpeg;base64,{processed_frame_base64}',
#                 'emotion': emotion,
#             }))
