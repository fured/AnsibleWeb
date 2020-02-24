#!/bin/env python 2.7
# -*- coding: utf-8 -*-

"""
Author: fured
Date: 2019.10.16
Desc: 做一些检查工作
"""

import logging as logger

from django.http import HttpResponse

def check_method(method):
    def func_outer(func_param):
        def func_inner(request, *arg):
            if method == request.method:                                                
                result = func_param(request, *arg)
                return result
            else:
                logger.warning("Vaild request method:%s for %s" % 
                        (request.method, request.path))
                return HttpResponse("Not support http method.")
        return func_inner
    return func_outer


