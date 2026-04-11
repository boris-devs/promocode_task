from decimal import Decimal

from rest_framework import serializers

from orders.models import Order, OrderItem
from users.models import User


class OrderGoodsCreateRequestSerializer(serializers.Serializer):
    good_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class OrderGoodsResponseSerializer(serializers.ModelSerializer):
    good_id = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(
        source="price_at_purchase", max_digits=10, decimal_places=2, read_only=True
    )
    discount = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["good_id", "quantity", "price", "discount", "total"]

    @staticmethod
    def _get_discount_percent(obj):
        return Decimal(getattr(obj, "discount_amount") or 0)

    def get_discount(self, obj):
        return self._get_discount_percent(obj) / Decimal("100")

    def get_total(self, obj):
        subtotal = obj.quantity * obj.price_at_purchase
        discount_ratio = self._get_discount_percent(obj) / Decimal("100")
        return (subtotal * (Decimal("1") - discount_ratio)).quantize(Decimal("0.01"))


class OrderCreateRequestSerializer(serializers.ModelSerializer):
    goods = OrderGoodsCreateRequestSerializer(many=True)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Order
        fields = ["user_id", "goods", "promo_code"]


class OrderCreateResponseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    order_id = serializers.IntegerField(source="id", read_only=True)
    goods = OrderGoodsResponseSerializer(source="items", many=True, read_only=True)
    price = serializers.DecimalField(
        source="total_price", max_digits=10, decimal_places=2, read_only=True
    )
    discount = serializers.SerializerMethodField()
    total = serializers.DecimalField(
        source="final_price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = ["user_id", "order_id", "goods", "price", "discount", "total"]

    def get_discount(self, obj):
        return Decimal(obj.discount or 0) / Decimal("100")
