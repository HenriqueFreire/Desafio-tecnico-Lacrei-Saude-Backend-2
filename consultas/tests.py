from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from profissionais.models import Professional
from .models import Appointment


class AppointmentTests(APITestCase):

    def setUp(self):
        # Criar usuário e autenticar
        self.user = User.objects.create_user(username='testuser', password='password')
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'password'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Criar um profissional para vincular às consultas
        self.professional = Professional.objects.create(
            social_name='Dr. Appointment Test',
            profession='General',
            address='Test Av',
            contact='999999')

    def test_create_appointment(self):
        url = reverse('appointment-list')
        future_date = timezone.now() + timedelta(days=1)
        data = {'professional': self.professional.id, 'date': future_date}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_create_appointment_past_date(self):
        url = reverse('appointment-list')
        past_date = timezone.now() - timedelta(days=1)
        data = {'professional': self.professional.id, 'date': past_date}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)

    def test_get_appointments_by_professional_id(self):
        # Criar uma consulta para o profissional
        Appointment.objects.create(professional=self.professional,
                                   date=timezone.now() + timedelta(days=2))

        # Criar outro profissional e uma consulta para ele
        other_prof = Professional.objects.create(social_name='Other Doctor',
                                                 contact='000',
                                                 profession='X',
                                                 address='Y')
        Appointment.objects.create(professional=other_prof,
                                   date=timezone.now() + timedelta(days=3))

        url = reverse('appointment-list')
        # Filtrar pelo ID do primeiro profissional
        response = self.client.get(f"{url}?professional_id={self.professional.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['professional'], self.professional.id)

    def test_duplicate_appointment_fails(self):
        url = reverse('appointment-list')
        date = timezone.now() + timedelta(days=5)
        data = {'professional': self.professional.id, 'date': date}
        # Criar a primeira consulta
        self.client.post(url, data, format='json')

        # Tentar criar outra no mesmo horário para o mesmo profissional
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_appointments_unauthenticated(self):
        url = reverse('appointment-list')
        self.client.credentials()  # Remove JWT token
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_appointment_invalid_professional(self):
        url = reverse('appointment-list')
        future_date = timezone.now() + timedelta(days=1)
        data = {'professional': 99999, 'date': future_date}  # Inexistent ID
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('consultas.services.asaas.requests.post')
    def test_create_appointment_with_successful_asaas_split(self, mock_post):
        # Configure mock for ASAAS success response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'pay_mock123456'}
        mock_post.return_value = mock_response

        # Add wallet ID to professional to trigger external payment call
        self.professional.asaas_wallet_id = 'wallet_mock_id'
        self.professional.save()

        url = reverse('appointment-list')
        future_date = timezone.now() + timedelta(days=1)
        data = {
            'professional': self.professional.id,
            'date': future_date,
            'value': '150.00'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        
        # Verify that payment ID was populated
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.asaas_payment_id, 'pay_mock123456')
        mock_post.assert_called_once()

    @patch('consultas.services.asaas.requests.post')
    def test_create_appointment_with_failed_asaas_split(self, mock_post):
        # Configure mock to raise a connection error
        mock_post.side_effect = Exception("Asaas sandbox API timeout")

        self.professional.asaas_wallet_id = 'wallet_mock_id'
        self.professional.save()

        url = reverse('appointment-list')
        future_date = timezone.now() + timedelta(days=1)
        data = {
            'professional': self.professional.id,
            'date': future_date,
            'value': '150.00'
        }
        response = self.client.post(url, data, format='json')

        # Booking should still succeed even if the payment provider is down
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        
        appointment = Appointment.objects.first()
        self.assertIsNone(appointment.asaas_payment_id)
