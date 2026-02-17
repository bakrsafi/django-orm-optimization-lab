import random
import time
from celery import shared_task
from django.db import transaction
from .models import Order, Product
from celery import chain


@shared_task
def start_order_workflow(order_id):

    workflow = chain(
        reserve_stock.s(order_id),
        charge_payment.s(),
        generate_invoice.s(),
        notify_shipping.s(),
    )

    workflow.delay()

@shared_task
def notify_shipping(order_id):
    order = Order.objects.get(id=order_id)
    order.status = Order.Status.SHIPPED
    order.save()


@shared_task
def generate_invoice(order_id):
    order = Order.objects.get(id=order_id)
    print(f"Invoice generated for order {order_id}")
    return order_id


@shared_task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=10)
def charge_payment(self, order_id):

    order = Order.objects.get(id=order_id)

    # simulate external gateway failure
    if random.random() < 0.3:
        raise ConnectionError("Payment provider timeout")

    order.status = Order.Status.PAID
    order.save()

    return order_id

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 5})
def reserve_stock(self, order_id):

    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order_id)
        product = order.product

        if product.stock < order.quantity:
            order.status = Order.Status.FAILED
            order.save()
            return

        product.stock -= order.quantity
        product.save()

        order.status = Order.Status.STOCK_RESERVED
        order.save()

    return order_id

@shared_task
def start_order_workflow(order_id):

    workflow = chain(
        reserve_stock.s(order_id),
        charge_payment.s(),
        generate_invoice.s(),
        notify_shipping.s(),
    )

    workflow.delay()



@shared_task
def send(message):
    print("Sending:", message)
    for x in range(10):
        time.sleep(1)
        print(x)
        x=x+1