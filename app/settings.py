#!/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Django settings for app project.
Generated by 'django-admin startproject' using Django 1.8.
For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import djcelery
import os
import logging

from kombu import Queue
from kombu import Exchange


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u7vy^_%y(bkt4)8^(^lh9e82s__(wjhhy_fky9%^ajqpy3i@$1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.models',
    'djcelery',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "ui")],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'AnsibleWeb',
        'USER': 'root',
        'PASSWORD': '1234567',
        'HOST': '192.168.0.1',
        'PORT': '3306',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "ui/static"),
)

# 自己项目的配置
HOSTS_FILE = {
    "path": "/saas/projects/AnsibleEye/inventory/",
    "file_name": "all_hosts.ini"
}

GROUPS_FILE = {
    "path": "/saas/projects/AnsibleEye/inventory/",
    "file_name": "group_hosts.ini"
}

ANSIBLE_DIR = "/saas/projects/AnsibleEye"
ANSIBLE_LOG_DIR = "/saas/projects/AnsibleEye/logs"
PACKAGE_ROOT_DIR = "/ci"
PLAYBOOK_DIR = "playbooks"

CSRF_COOKIE_HTTPONLY=True
CSRF_COOKIE_SECURE=True

djcelery.setup_loader()
CELERY_IMPORTS = ["app.tasks"]
CELERY_TIMEZONE = TIME_ZONE
BROKER_URL = 'redis://127.0.0.1:6379/10'
CELERY_DEFAULT_QUEUE = "ansible_task"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TRACK_STARTED = True
CELERY_QUEUES = (
    Queue("ansible_task", exchange=Exchange("ansible_task"), routing_key="ansible_task"),        
    Queue("ansible_task_check", exchange=Exchange("ansible_task_check"), routing_key="ansible_task_check"),        
)
CELERY_ROUTES = {
    "run-task-set": {"queue": "ansible_task", "routing_key": "ansible_task"},
    "check-task-set": {"queue": "ansible_task_check", "routing_key": "ansible_task_check"}
}
CELERY_DEFAULT_QUEUE = "ansible_task"
CELERY_DEFAULT_EXCHANGE = "ansible_task"
CELERY_DEFAULT_ROUTING_KEY = "ansible_task"

TASK_STATUS = ["PENDING", "STARTED", "COMPLETE", "FAILURE", "REVOKED", "NEW"]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', 
    filename='/saas/projects/AnsibleWeb/logs/web/api.log',
    filemode='a')
