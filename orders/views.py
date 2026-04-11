from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import (
    OrderCreateRequestSerializer,
    OrderCreateResponseSerializer,
)
from orders.services import OrderService


class OrderCreateView(CreateAPIView):
    serializer_class = OrderCreateRequestSerializer
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.create_order(serializer.validated_data)
        response_serializer = OrderCreateResponseSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
