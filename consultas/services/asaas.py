import requests
import os
import logging

logger = logging.getLogger(__name__)


class AsaasService:
    BASE_URL = "https://sandbox.asaas.com/api/v3"
    API_KEY = os.environ.get('ASAAS_API_KEY')

    @classmethod
    def process_appointment_payment(cls, appointment):
        """
        Gera uma cobrança com split para o profissional vinculado à consulta.
        O Asaas dividirá o valor automaticamente.
        """
        if not appointment.professional.asaas_wallet_id:
            logger.error(
                f"Professional {appointment.professional.id} has no Asaas Wallet ID")
            return None

        payload = {
            "customer":
            "cus_000000000000",  # Em prod, seria o ID do paciente no Asaas
            "billingType":
            "PIX",
            "value":
            float(appointment.value),
            "dueDate": (appointment.date).strftime('%Y-%m-%d'),
            "description":
            f"Consulta Lacrei Saúde - {appointment.professional.social_name}",
            "split": [{
                "walletId": appointment.professional.asaas_wallet_id,
                "percentualValue":
                80.0  # Exemplo: 80% para o profissional, 20% para Lacrei
            }]
        }

        headers = {"access_token": cls.API_KEY, "Content-Type": "application/json"}

        try:
            response = requests.post(f"{cls.BASE_URL}/payments",
                                     json=payload,
                                     headers=headers)
            response.raise_for_status()
            data = response.json()
            appointment.asaas_payment_id = data.get('id')
            appointment.save()
            return data
        except Exception as e:
            logger.error(f"Error processing Asaas split: {str(e)}")
            return None
