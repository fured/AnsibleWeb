#!/bin/ens python2.7
# -*- coding: utf-8 -*-

"""
Author: fured
Date: 2019.10.16
Desc: 用户相关view
"""

import json
import logging as logger

from app.common.check import check_method
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
@check_method("GET")
def login(request):
    print request.method
    return HttpResponse("login html page.")


@ensure_csrf_cookie
@check_method("GET")
def index(requests):
    return render_to_response("index.html")
