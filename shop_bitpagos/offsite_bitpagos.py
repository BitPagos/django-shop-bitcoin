# -*- coding: utf-8 -*-
__author__ = 'sserrano'

import logging
import json
from decimal import Decimal

from django.conf import settings
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

from django.views.decorators.csrf import csrf_exempt
from shop_bitpagos.models import Checkout


import requests

class fakefloat(float):
    def __init__(self, value):
        self._value = value
    def __repr__(self):
        return str(self._value)

def defaultencode(o):
    if isinstance(o, Decimal):
        # Subclass float with custom repr?
        return fakefloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")


class ConfigError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

BITPAGOS_BACKEND_URL = getattr(settings, 'SHOP_BITPAGOS_BACKEND_URL', 'https://www.bitpagos.net')
BACKEND_NAME = "BitPagos"
class BitPagosBackend(object):
    '''
    A django-shop payment backend for the stripe service, this
    is the workhorse view. It processes what the CardForm class
    kicks back to the server.

    It also saves the customer billing information for later use.
    '''
    backend_name = BACKEND_NAME
    url_namespace = "bitpagos"

    def __init__(self, shop):
        self.shop = shop
        self.key = getattr(settings, 'SHOP_BITPAGOS_KEY', None)
        self.currency = getattr(settings, 'SHOP_BITPAGOS_CURRENCY', 'USD')

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.bitpagos_payment_view, name='bitpagos' ),
            url(r'^success/$', self.bitpagos_return_successful_view, name='bitpagos_success' ),
            url(r'^ipn/$', self.bitpagos_ipn_update, name='bitpagos_ipn' ),
        )
        return urlpatterns

    def bitpagos_payment_view(self, request):
        order = self.shop.get_order(request)
        order_id = self.shop.get_order_unique_id(order)
        amount = self.shop.get_order_total(order)

        if self.key is None:
            raise ConfigError('You must set SHOP_BITPAGOS_KEY in your configuration file.')

        items = []
        for item in order.items.all():
            items.append({
                'unit_price': str(item.unit_price),
                'quantity': item.quantity,
                'title': item.product_name if item.product_name else "item %s" % item.id
            })

        checkout = {
            "currency": self.currency,
            "amount": str(amount),
            "items": items,
            "reference_id" : order_id,
            "return_success": request.build_absolute_uri(reverse("bitpagos_success")),
            "return_cancel": request.build_absolute_uri(reverse("checkout_confirm")),
            "return_pending": request.build_absolute_uri(reverse("bitpagos_success")),
        }

        if request.user.is_authenticated():
            checkout['first_name'] = request.user.first_name
            checkout['last_name'] = request.user.last_name
            checkout['email'] = request.user.email

        dump = json.dumps(checkout, default=defaultencode)
        logging.info(json.dumps(dump))
        r = requests.post(url="%s%s" % (BITPAGOS_BACKEND_URL, "/api/v1/checkout/"),
                          data=dump,
                          headers={'Authorization': 'ApiKey %s' % self.key,
                                   'Content-Type': 'application/json'})
        logging.info(r.content)

        if r.status_code != 201:
            logging.error("error calling bitpagos %s" % r.content)
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        data = r.json()
        obj, created = Checkout.objects.get_or_create(order=order, uuid=data['uuid'])
        obj.update(data)

        return HttpResponseRedirect(data['checkout_url'])

    def bitpagos_return_successful_view(self, request):
        return HttpResponseRedirect(self.shop.get_finished_url())

    @csrf_exempt
    def bitpagos_ipn_update(self, request):

        if request.method != "POST":
            return HttpResponse("")

        if not request.POST[u'resource_uri'].startswith("/api/v1/checkout/"):
            return HttpResponse("")

        r = requests.get(url="%s%s" % (BITPAGOS_BACKEND_URL, request.POST[u'resource_uri']),
                         headers={'Authorization': 'ApiKey %s' % self.key,
                                  'Content-Type': 'application/json'})

        data = r.json()
        checkout = Checkout.objects.get(uuid=data['uuid'])
        checkout.update(data)

        return HttpResponse("ok")

