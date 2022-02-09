from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class SigninTests(TestCase):

    @staticmethod
    def create_test_user() -> dict:
        user_data = {
            "email": "user@user.com",
            "password": "secret",
        }
        UserModel = get_user_model()
        UserModel.objects.create_user('user@user.com', 'secret')
        return user_data

    def test_signin_url_exists_at_desired_location(self) -> None:
        response = self.client.get('/users/login/')
        self.assertEqual(response.status_code, 200)

    def test_signin_url_accessible_by_name(self) -> None:
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_signin_url_uses_correct_template(self) -> None:
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_auth_success_without_next_param(self):
        """Проверяет авторизацию с использованием корректных данных, без параметра next"""
        user_data = self.create_test_user()
        response = self.client.post(reverse('login'), data={
            "username": user_data['email'],
            "password": user_data['password'],
        }, follow=True)
        self.assertRedirects(response, reverse('cases-list'))

    def test_auth_success_with_next_param(self):
        """Проверяет авторизацию с использованием корректных данных, с параметром next"""
        user_data = self.create_test_user()
        response = self.client.post(f"{reverse('login')}?next=/some_link/", data={
            "username": user_data['email'],
            "password": user_data['password'],
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/some_link/')

    def test_auth_fail(self):
        """Проверяет авторизацию с использованием некорректных данных."""
        response = self.client.post(reverse('login'), data={
            "username": 'wrong_email@user.com',
            "password": 'secret',
        })
        self.assertEqual(response.status_code, 200)

        expected_error = 'Будь ласка, введіть правильні email-адресу та пароль'
        self.assertContains(response, expected_error)
