from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from django.conf import settings


class Promocode(models.Model):
    code = models.CharField(max_length=255)
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    quantity = models.PositiveIntegerField()
    expiration_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField(
        "goods.Category",
        blank=True,
        related_name="promocodes",
        help_text="Categories for which the promocode is valid")
    created_at = models.DateTimeField(auto_now_add=True)


class PromocodeUsage(models.Model):
    promo_code = models.ForeignKey(Promocode, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
