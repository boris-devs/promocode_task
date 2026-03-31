from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class OrderItem(models.Model):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)
    good = models.ForeignKey("goods.Good", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.IntegerField(name="discount in percent", default=0,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)])


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    promo_code = models.ForeignKey("promocodes.Promocode", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField(help_text="total discount in percent", default=0,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)])
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
