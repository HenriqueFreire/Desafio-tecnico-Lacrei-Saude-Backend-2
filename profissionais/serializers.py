from rest_framework import serializers
from .models import Professional


class ProfessionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Professional
        fields = '__all__'

    def validate_social_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Social name must have at least 3 characters.")
        return value
