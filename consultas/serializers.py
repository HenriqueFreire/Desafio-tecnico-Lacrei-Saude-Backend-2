from rest_framework import serializers
from django.utils import timezone
from .models import Appointment
from rest_framework.validators import UniqueTogetherValidator


class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Appointment.objects.all(),
                fields=['professional', 'date'],
                message="This professional already has an appointment at this time.")
        ]

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value
