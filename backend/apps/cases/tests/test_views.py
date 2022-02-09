from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class CasesListNonAuthTests(TestCase):
    def test_cases_list_requires_authorization(self) -> None:
        """Проверяет что доступа у неавторизированных пользователей нет."""
        resp = self.client.get('', follow=True)
        self.assertRedirects(resp, '/users/login/?next=/')


class CasesListTests(TestCase):
    def setUp(self) -> None:
        # Авторизация пользователя
        UserModel = get_user_model()
        UserModel.objects.create_user('user@user.com', 'secret')
        self.client.login(email='user@user.com', password='secret')

    def test_cases_list_url_exists_at_desired_location(self) -> None:
        resp = self.client.get('')
        self.assertEqual(resp.status_code, 200)

    def test_cases_list_accessible_by_name(self) -> None:
        resp = self.client.get(reverse('cases-list'))
        self.assertEqual(resp.status_code, 200)

    def test_cases_list_uses_correct_template(self) -> None:
        resp = self.client.get(reverse('cases-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'cases/list/index.html')
