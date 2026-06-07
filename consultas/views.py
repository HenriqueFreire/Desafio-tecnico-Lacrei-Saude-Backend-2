from rest_framework import viewsets
from .models import Appointment
from .serializers import AppointmentSerializer
from .services.asaas import AsaasService


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = Appointment.objects.all()
        professional_id = self.request.query_params.get('professional_id')

        if professional_id is not None:
            queryset = queryset.filter(professional_id=professional_id)

        return queryset

    def perform_create(self, serializer):
        appointment = serializer.save()
        # Dispara o processamento do pagamento
        AsaasService.process_appointment_payment(appointment)
