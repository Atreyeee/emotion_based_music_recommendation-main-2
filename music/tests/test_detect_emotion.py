import base64
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# A 1x1 transparent PNG, valid enough for cv2.imdecode to accept as bytes
# even though it's not a real photo — the view under test mocks out the
# actual face/emotion detection, so decodability is all that matters here.
TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class DetectEmotionTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="carol", password="password123")
        self.client.login(username="carol", password="password123")
        self.url = reverse("detect-emotion")

    def _post_frame(self, frame_value="data:image/png;base64," + TINY_PNG_BASE64):
        return self.client.post(self.url, data=json.dumps({"frame": frame_value}), content_type="application/json")

    def test_missing_frame_returns_400(self):
        response = self.client.post(self.url, data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_returns_400(self):
        response = self.client.post(self.url, data="not json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_undecodable_frame_returns_400(self):
        response = self._post_frame(frame_value="data:image/png;base64,bm90LWEtcmVhbC1pbWFnZQ==")
        self.assertEqual(response.status_code, 400)

    @patch("music.views.process_frame")
    def test_detected_emotion_includes_playlist_url(self, mock_process_frame):
        mock_process_frame.return_value = (None, "happy", {"x": 10, "y": 10, "width": 50, "height": 50})

        response = self._post_frame()
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["emotion"], "happy")
        self.assertEqual(body["playlist_url"], reverse("playlist", args=["happy"]))

    @patch("music.views.process_frame")
    def test_no_face_detected_returns_null_playlist(self, mock_process_frame):
        mock_process_frame.return_value = (None, None, None)

        response = self._post_frame()
        body = response.json()
        self.assertIsNone(body["emotion"])
        self.assertIsNone(body["playlist_url"])
