__author__ = 'sserrano'

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import requests

from shop_bitpagos.models import Checkout

BITPAGOS_BACKEND_URL = getattr(settings, 'SHOP_BITPAGOS_BACKEND_URL', 'https://www.bitpagos.net')
BITPAGOS_KEY = getattr(settings, 'SHOP_BITPAGOS_KEY', None)



class Command(BaseCommand):
    args = ''
    help = 'Check order status'

    def handle(self, *args, **options):

        if BITPAGOS_KEY is None:
            self.stdout.write("missing SHOP_BITPAGOS_KEY")
            return

        for checkout in Checkout.objects.filter(order__status__lt=40):
            r = requests.get(url="%s/api/v1/checkout/%s/" % (BITPAGOS_BACKEND_URL, checkout.uuid),
                             headers={'Authorization': 'ApiKey %s' % BITPAGOS_KEY,
                                      'Content-Type': 'application/json'})
            if r.status_code == 200:
                checkout.update(r.json())

        self.stdout.write("")

