from django.db import models

from django.conf import settings


class Promocode(models.Model):
    code = models.CharField(max_length=255)
    discount = models.IntegerField()
    quantity = models.PositiveIntegerField()
    expiration_date = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PromocodeUsage(models.Model):
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)