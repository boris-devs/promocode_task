from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Good(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='goods')
    quantity = models.PositiveIntegerField()
    is_promo_allowed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)