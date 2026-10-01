from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from music.views import MOOD_REGISTRY


class MoodUrlUniquenessTests(TestCase):
    """Regression test for the original bug: `api/songs/` was registered
    six times with the same path and the same URL name, so Django only
    ever resolved to the first (Neutral) view — the other five moods'
    API endpoints were permanently unreachable. Each mood must now
    resolve to its own distinct URL.
    """

    def test_each_mood_has_a_distinct_playlist_url(self):
        urls = {reverse("playlist", args=[mood]) for mood in MOOD_REGISTRY}
        self.assertEqual(len(urls), len(MOOD_REGISTRY))

    def test_each_mood_has_a_distinct_api_url(self):
        urls = {reverse("song-list", args=[mood]) for mood in MOOD_REGISTRY}
        self.assertEqual(len(urls), len(MOOD_REGISTRY))


class PlaylistViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="password123")
        self.client.login(username="bob", password="password123")

    def test_valid_mood_renders(self):
        response = self.client.get(reverse("playlist", args=["happy"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HAPPY PLAYLIST")

    def test_unknown_mood_redirects_to_webcam(self):
        response = self.client.get(reverse("playlist", args=["ecstatic"]), follow=True)
        self.assertRedirects(response, reverse("webcam"))
        self.assertContains(response, "Unknown mood")


class MoodSongApiTests(TestCase):
    def test_valid_mood_returns_200(self):
        response = self.client.get(reverse("song-list", args=["sad"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_unknown_mood_returns_404(self):
        response = self.client.get(reverse("song-list", args=["nonexistent"]))
        self.assertEqual(response.status_code, 404)
