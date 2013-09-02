#-*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

CLASSIFIERS = []

setup(
    author="Sebastian Serrano",
    author_email="support@bitpagos.net",
    name='django-shop-bitpagos',
    version='0.1',
    description='BitPagos Bitcoin Payment Backend for Django Shop',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://www.bitpagos.net/',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.2',
        'requests',
    ],
    packages=find_packages(exclude=["example", "example.*"]),
    zip_safe=False
)
