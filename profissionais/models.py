from django.db import models


class Professional(models.Model):
    social_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=100)
    address = models.TextField()
    contact = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    asaas_wallet_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Professionals"
        constraints = [
            models.UniqueConstraint(fields=['social_name'],
                                    name='unique_professional_social_name_v2')
        ]

    def __str__(self):
        return self.social_name
