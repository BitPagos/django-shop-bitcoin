django-shop-bitcoin
===================

BitPagos Bitcoin Payment Backend for Django Shop

This applicaiton is a bitpagos backend for django-SHOP, or any other shop system implementing its shop interface.

Usage
======

1.
Add django-paypal and this project to your INSTALLED_APPS:::

  INSTALLED_APPS = (
  ...
  'shop_bitpagos',
  ...
  )

2.
Add 'shop_bitpagos.offsite_bitpagos.BitPagosBackend' to django-SHOP's SHOP_PAYMENT_BACKENDS setting.

3.
Make sure you set following in settings.py:

* `SHOP_BITPAGOS_KEY`   #found it at https://www.bitpagos.net/api/settings/

Optional settings:

* `SHOP_BITPAGOS_CURRENCY`   #default USD 

4.
Set bitpagos notification url to:
http://www.yoursite.com/shop/pay/bitpagos/ipn/    # /shop depends on the prefix used for django-shop

5.
Set a cron to run periodically:

python manage.py bitpagos_check

Contributing
=============

Feel free to write any comment or suggestion for this project to sebastian@bitpagos.net

