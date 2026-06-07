from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Professional


class ProfessionalTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        # Obter token JWT
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'password'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_professional(self):
        url = reverse('professional-list')
        data = {
            'social_name': 'Dr. Test',
            'profession': 'Developer',
            'address': 'Nix Street, 123',
            'contact': '123456789'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Professional.objects.count(), 1)

    def test_duplicate_social_name_fails(self):
        url = reverse('professional-list')
        data = {
            'social_name': 'Dr. Duplicate',
            'profession': 'General',
            'address': 'Street 1',
            'contact': '111'
        }
        # Criar o primeiro
        self.client.post(url, data, format='json')

        # Tentar criar o segundo com o mesmo nome social
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('social_name', response.data)

    def test_get_professionals_list(self):
        url = reverse('professional-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_professionals_list_unauthenticated(self):
        url = reverse('professional-list')
        self.client.credentials()  # Remove credentials
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_professionals_list_invalid_token(self):
        url = reverse('professional-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_value')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_professional_invalid_payload(self):
        url = reverse('professional-list')
        # Nome social deve ter pelo menos 3 caracteres
        data = {
            'social_name': 'Dr',
            'profession': 'General',
            'address': 'Street 1',
            'contact': '123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('social_name', response.data)
