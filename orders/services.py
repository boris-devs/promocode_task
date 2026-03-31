from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from goods.models import Good
from promocodes.models import Promocode, PromocodeUsage

from .models import Order, OrderItem


class OrderService:
    @staticmethod
    def create_order(order_data: dict):
        with transaction.atomic():
            user_obj = order_data["user"]
            promo_code = (order_data.get("promo_code") or "").strip()
            goods_payload = order_data["goods"]

            goods_quantities = {}
            for item in goods_payload:
                good_id = item["good_id"]
                quantity = item["quantity"]
                if quantity <= 0:
                    raise ValidationError({"goods": f"Quantity for good {good_id} must be greater than 0"})

                #Even if we receive duplicate good_ids, we will sum their quantities
                goods_quantities[good_id] = goods_quantities.get(good_id, 0) + quantity

            requested_ids = set(goods_quantities.keys())
            goods_qs = Good.objects.select_related("category").filter(id__in=requested_ids)
            goods_by_id = {good.id: good for good in goods_qs}

            missing_ids = sorted(requested_ids - set(goods_by_id.keys()))
            if missing_ids:
                raise ValidationError({"goods": f"Missing goods with ids: {missing_ids}"})

            promo = None
            discount_percent = 0
            eligible_good_ids = set()

            if promo_code:
                promo = Promocode.objects.select_for_update().filter(code=promo_code, active=True).first()
                if not promo:
                    raise ValidationError({"promo_code": "Promo code does not exist or inactive"})

                if promo.expiration_date < timezone.now():
                    raise ValidationError({"promo_code": "Promo code is expired"})

                if promo.quantity < 1:
                    raise ValidationError({"promo_code": "Promo code usage limit reached"})

                if PromocodeUsage.objects.filter(promo_code=promo, user=user_obj).exists():
                    raise ValidationError({"promo_code": "Promo code already used by this user"})

                has_category_limit = promo.categories.exists()
                allowed_category_ids = set()
                if has_category_limit:
                    allowed_category_ids = set(promo.categories.values_list("id", flat=True))

                for good in goods_by_id.values():
                    if not good.is_promo_allowed:
                        continue
                    if has_category_limit and good.category_id not in allowed_category_ids:
                        continue
                    eligible_good_ids.add(good.id)

                if not eligible_good_ids:
                    raise ValidationError({"promo_code": "Promo code is not applicable to selected goods"})

                discount_percent = promo.discount

            order = Order.objects.create(
                user=user_obj,
                promo_code=promo,
                total_price=Decimal("0.00"),
                discount=discount_percent,
                final_price=Decimal("0.00"),
            )

            total_price = Decimal("0.00")
            final_price = Decimal("0.00")

            for good_id, quantity in goods_quantities.items():
                good = goods_by_id[good_id]
                price = good.price * quantity
                item_discount = discount_percent if good_id in eligible_good_ids else 0
                discount_ratio = Decimal(item_discount) / Decimal("100")
                total = price * (Decimal("1") - discount_ratio)

                total_price += price
                final_price += total

                OrderItem.objects.create(
                    order=order,
                    good=good,
                    quantity=quantity,
                    price_at_purchase=good.price,
                    discount_amount=item_discount,
                )

            order.total_price = total_price
            order.final_price = final_price
            order.save(update_fields=["total_price", "final_price", "discount"])

            if promo:
                Promocode.objects.filter(id=promo.id).update(quantity=F("quantity") - 1)
                PromocodeUsage.objects.create(promo_code=promo, user=user_obj)

            return order
