#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="jsonfix",
    version='0.0.1',
    author="Nozomu Kaneko",
    author_email="nozom.kaneko@gmail.com",
    url="http://github.com/knzm/python-jsonfix",
    license="MIT License",
    py_modules=['jsonfix'],
    platforms=['any'],
    zip_safe=True,
)
