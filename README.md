# Promocode Task

Django REST API for creating orders with optional promo code discounts.

## Stack
- Python 3.12+
- Django 6
- Django REST Framework
- SQLite

## Run locally
```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

## Main endpoint
- `POST /orders/` - create order with goods and optional promo code.

Example request:
```json
{
  "user_id": 1,
  "goods": [
    {"good_id": 1, "quantity": 2},
    {"good_id": 2, "quantity": 1}
  ],
  "promo_code": "SUMMER2026"
}
```

Response includes: `order_id`, items, original price, discount, and final total.

## Tests
```bash
uv run python manage.py test
```
