from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from goods.models import Category, Good
from orders.services import OrderService
from promocodes.models import Promocode, PromocodeUsage
from users.models import User


class OrderServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass")
        self.category_1 = Category.objects.create(name="C1")
        self.category_2 = Category.objects.create(name="C2")

        self.good_allowed = Good.objects.create(
            name="allowed",
            price=Decimal("100.00"),
            category=self.category_1,
            quantity=10,
            is_promo_allowed=True,
        )
        self.good_blocked = Good.objects.create(
            name="blocked",
            price=Decimal("50.00"),
            category=self.category_1,
            quantity=10,
            is_promo_allowed=False,
        )
        self.good_other_category = Good.objects.create(
            name="other",
            price=Decimal("70.00"),
            category=self.category_2,
            quantity=10,
            is_promo_allowed=True,
        )

        self.promo = Promocode.objects.create(
            code="SUMMER2025",
            discount=10,
            quantity=2,
            expiration_date=timezone.now() + timedelta(days=3),
            active=True,
        )
        self.promo.categories.set([self.category_1])

    def test_create_order_without_promo(self):
        order = OrderService.create_order(
            {
                "user": self.user,
                "goods": [{"good_id": self.good_allowed.id, "quantity": 2}],
            }
        )

        self.assertEqual(order.total_price, Decimal("200.00"))
        self.assertEqual(order.final_price, Decimal("200.00"))
        self.assertEqual(order.discount, 0)

    def test_non_existing_promo_raises_error(self):
        with self.assertRaises(ValidationError):
            OrderService.create_order(
                {
                    "user": self.user,
                    "goods": [{"good_id": self.good_allowed.id, "quantity": 1}],
                    "promo_code": "NOPE",
                }
            )

    def test_expired_promo_raises_error(self):
        self.promo.expiration_date = timezone.now() - timedelta(days=1)
        self.promo.save(update_fields=["expiration_date"])

        with self.assertRaises(ValidationError):
            OrderService.create_order(
                {
                    "user": self.user,
                    "goods": [{"good_id": self.good_allowed.id, "quantity": 1}],
                    "promo_code": self.promo.code,
                }
            )

    def test_user_cannot_use_same_promo_twice(self):
        OrderService.create_order(
            {
                "user": self.user,
                "goods": [{"good_id": self.good_allowed.id, "quantity": 1}],
                "promo_code": self.promo.code,
            }
        )

        with self.assertRaises(ValidationError):
            OrderService.create_order(
                {
                    "user": self.user,
                    "goods": [{"good_id": self.good_allowed.id, "quantity": 1}],
                    "promo_code": self.promo.code,
                }
            )

    def test_promo_applies_only_to_allowed_goods(self):
        order = OrderService.create_order(
            {
                "user": self.user,
                "goods": [
                    {"good_id": self.good_allowed.id, "quantity": 2},
                    {"good_id": self.good_blocked.id, "quantity": 1},
                    {"good_id": self.good_other_category.id, "quantity": 1},
                ],
                "promo_code": self.promo.code,
            }
        )

        self.assertEqual(order.total_price, Decimal("320.00"))
        self.assertEqual(order.final_price, Decimal("300.00"))
        self.assertEqual(order.discount, 10)

        self.promo.refresh_from_db()
        self.assertEqual(self.promo.quantity, 1)
        self.assertTrue(PromocodeUsage.objects.filter(promo_code=self.promo, user=self.user).exists())
