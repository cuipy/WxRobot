#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from threading import Thread

def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper