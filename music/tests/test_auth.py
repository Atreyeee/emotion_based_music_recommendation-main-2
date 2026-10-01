from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SignupTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "newuser", "email": "new@example.com", "password1": "password123", "password2": "password123"},
        )
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertRedirects(response, reverse("webcam"))

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "newuser2", "email": "new2@example.com", "password1": "password123", "password2": "different"},
            follow=True,
        )
        self.assertFalse(User.objects.filter(username="newuser2").exists())
        self.assertContains(response, "do not match")

    def test_signup_rejects_short_password(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "shortpw", "email": "s@example.com", "password1": "short", "password2": "short"},
            follow=True,
        )
        self.assertFalse(User.objects.filter(username="shortpw").exists())
        self.assertContains(response, "at least 8 characters")

    def test_signup_rejects_duplicate_username(self):
        User.objects.create_user(username="taken", password="password123")
        response = self.client.post(
            reverse("signup"),
            {"username": "taken", "email": "dup@example.com", "password1": "password123", "password2": "password123"},
            follow=True,
        )
        self.assertContains(response, "taken")


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")

    def test_login_success_redirects_to_webcam(self):
        response = self.client.post(reverse("login"), {"username": "alice", "password": "password123"})
        self.assertRedirects(response, reverse("webcam"))

    def test_login_wrong_password_rejected(self):
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "wrong-password"}, follow=True
        )
        self.assertContains(response, "Invalid username or password")

    def test_logout_actually_logs_out(self):
        """Regression test for the original `def logout(request): pass` bug
        — this must clear the session, not just redirect while leaving the
        user authenticated.
        """
        self.client.login(username="alice", password="password123")
        self.client.get(reverse("logout"))

        response = self.client.get(reverse("webcam"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('webcam')}")


class RouteProtectionTests(TestCase):
    def test_webcam_requires_login(self):
        response = self.client.get(reverse("webcam"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('webcam')}")

    def test_playlist_requires_login(self):
        response = self.client.get(reverse("playlist", args=["happy"]))
        self.assertRedirects(response, f"{reverse('login')}?next=/playlist/happy/")
