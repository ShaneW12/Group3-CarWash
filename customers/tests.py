from django.test import TestCase
import re

from urllib.parse import urlsplit

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@override_settings(
    MAILERS={
        "default": {
            "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
        }
    },
    DEFAULT_FROM_EMAIL="cleanride@example.com",
    PASSWORD_RESET_TIMEOUT=1800,
)
class PasswordResetTests(TestCase):

    def setUp(self):
        self.old_password = "OriginalPassword123!"
        self.new_password = "UpdatedSecurePassword456!"

        self.user = get_user_model().objects.create_user(
            username="resetcustomer",
            email="resetcustomer@example.com",
            password=self.old_password,
            first_name="Test",
            last_name="Customer",
            phone="5551234567",
        )

        self.reset_url = reverse("password_reset")

        self.uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        self.token = default_token_generator.make_token(
            self.user
        )

        self.confirm_url = reverse(
            "password_reset_confirm",
            kwargs={
                "uidb64": self.uid,
                "token": self.token,
            },
        )

    # Test 1: Forgot password page loads
    def test_forgot_password_page_loads(self):
        response = self.client.get(self.reset_url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "forgot_password.html"
        )

    # Test 2: Registered email redirects correctly
    def test_registered_email_redirects(self):
        response = self.client.post(
            self.reset_url,
            {"email": self.user.email}
        )

        self.assertRedirects(
            response,
            reverse("password_reset_done")
        )

    # Test 3: Password reset email is generated
    def test_password_reset_email_sent(self):
        self.client.post(
            self.reset_url,
            {"email": self.user.email}
        )

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(
            mail.outbox[0].to,
            [self.user.email]
        )

        self.assertEqual(
            mail.outbox[0].subject,
            "Reset Your CleanRide Password"
        )

        self.assertIn(
            "/reset-password/",
            mail.outbox[0].body
        )

    # Test 4: Unknown email does not send a message
    def test_unregistered_email(self):
        response = self.client.post(
            self.reset_url,
            {"email": "unknown@example.com"}
        )

        self.assertRedirects(
            response,
            reverse("password_reset_done")
        )

        self.assertEqual(len(mail.outbox), 0)

    # Test 5: Valid token displays reset form
    def test_valid_reset_token(self):
        response = self.client.get(
            self.confirm_url,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["validlink"])

        self.assertTemplateUsed(
            response,
            "password_reset_confirm.html"
        )

    # Test 6: Invalid token is rejected
    def test_invalid_reset_token(self):
        invalid_url = reverse(
            "password_reset_confirm",
            kwargs={
                "uidb64": self.uid,
                "token": "invalid-token",
            },
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["validlink"])

    # Test 7: Mismatched passwords are rejected
    def test_mismatched_passwords(self):
        response = self.client.get(self.confirm_url)

        response = self.client.post(
            response.url,
            {
                "new_password1": self.new_password,
                "new_password2": "DifferentPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            response.context["form"].errors
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(self.old_password)
        )

    # Test 8: Complete password reset using emailed link
    def test_successful_password_reset(self):
        self.client.post(
            self.reset_url,
            {"email": self.user.email}
        )

        self.assertEqual(len(mail.outbox), 1)

        # Extract the actual reset link from the email.
        match = re.search(
            r"https?://\S+/reset-password/\S+",
            mail.outbox[0].body
        )

        self.assertIsNotNone(match)

        reset_path = urlsplit(match.group(0)).path

        response = self.client.get(reset_path)

        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            response.url,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        self.assertRedirects(
            response,
            reverse("password_reset_complete")
        )

        # Verify that the database contains the new password.
        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(self.new_password)
        )

        self.assertFalse(
            self.user.check_password(self.old_password)
        )

    # Test 9: Old password no longer authenticates
    def test_old_password_rejected(self):
        response = self.client.get(self.confirm_url)

        self.client.post(
            response.url,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        user = authenticate(
            email=self.user.email,
            password=self.old_password
        )

        self.assertIsNone(user)

    # Test 10: New password successfully authenticates
    def test_new_password_authentication(self):
        response = self.client.get(self.confirm_url)

        self.client.post(
            response.url,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        user = authenticate(
            email=self.user.email,
            password=self.new_password
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    # Test 11: Used reset link cannot be reused
    def test_reset_token_cannot_be_reused(self):
        response = self.client.get(self.confirm_url)

        self.client.post(
            response.url,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        response = self.client.get(self.confirm_url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["validlink"])
# Create your tests here.
