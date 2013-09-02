import json
import logging

from django.db import models

from shop.models import Order
from shop.payment.api import PaymentAPI

BACKEND_NAME = "BitPagos"

CHECKOUT_CHOICES = (
    ('WA', 'waiting'),
    ('PE', 'Pending'),
    ('PA', 'Paid'),
    ('CO', 'Complete'),
)




class Checkout(models.Model):
    order = models.ForeignKey(Order)
    uuid = models.CharField(max_length=32)
    status = models.CharField(max_length=3, choices=CHECKOUT_CHOICES)
    extra = models.TextField()

    def update(self, data):
        self.status = data['status']
        self.extra = json.dumps(data)
        self.save()
        order = self.order

        if order.status < 40 and data['status'] in ['PA', 'CO']:
            logging.info("confirmed %s" % order.id)
            shop = PaymentAPI()
            shop.confirm_payment(order=order, amount=data['amount'], transaction_id=data['uuid'],
                                 payment_method=BACKEND_NAME)

