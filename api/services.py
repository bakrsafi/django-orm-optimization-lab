
from django.db import transaction
from .models import Order, Product
from .tasks import start_order_workflow

def create_order(product_id, quantity):

    with transaction.atomic():

        product = Product.objects.select_for_update().get(id=product_id)

        if product.stock < quantity:
            raise Exception("Out of stock")

        order = Order.objects.create(
            product=product,
            quantity=quantity,
        )

        # لاحظ هنا
        transaction.on_commit(
            lambda: start_order_workflow.delay(order.id)
        )

    return order
