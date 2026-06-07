from django.db import models
from profissionais.models import Professional


class Appointment(models.Model):
    professional = models.ForeignKey(Professional,
                                     on_delete=models.CASCADE,
                                     related_name='appointments')
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, default='PENDING')
    asaas_payment_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['professional', 'date'],
                                    name='unique_appointment_slot_v2')
        ]

    def __str__(self):
        return f"Appointment with {self.professional.social_name} on {self.date}"
