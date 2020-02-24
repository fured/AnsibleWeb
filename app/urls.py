#!/bin/python 2.7
# -*- coding: utf-8 -*-

from app.views import account
from app.views import inventory
from app.views import tasks
from app.views import playbook

from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)), 
    url(r'^inventory/add/host', inventory.add_host),
    url(r'^inventory/add/group', inventory.add_group),
    url(r'^inventory/update/hostfile', inventory.gen_host_file),
    url(r'^inventory/update/groupfile', inventory.gen_group_file),
    url(r'^inventory/getdata/allgroup', inventory.get_data_group),
    url(r'^inventory/getdata/childgroup', inventory.get_data_childgroup),
    url(r'^inventory/getdata/hostdata', inventory.get_data_host),
    url(r'^inventory/delete', inventory.delete_inventory),
    url(r'^account/login', account.login),
    url(r'^tasks/package/update', tasks.update_package),
    url(r'^tasks/taskset/obtaindata', tasks.get_taskset_data),
    url(r'^tasks/taskset/obtaintasks', tasks.get_tasks_data),
    url(r'^tasks/taskset/getalldata', tasks.get_all_data),
    url(r'^tasks/taskset/payload', tasks.payload_task_set),
    url(r'^tasks/taskset/runcheck', tasks.run_check_task_set),
    url(r'^tasks/taskset/currentstatus', tasks.task_set_status),
    url(r'^tasks/taskset/getrunlog', tasks.get_task_log),
    url(r'^tasks/taskset/getchecklog', tasks.get_check_log),
    url(r'^tasks/taskset/revoke', tasks.task_set_revoke),
    url(r'^playbook/yml/register', playbook.register_yml),
    url(r'^playbook/getdata/all', playbook.get_data_all),
    url(r'^playbook/getdata/ymldetail', playbook.get_data_ymldetail),
    url(r'^playbook/getdata/hostgroups', playbook.get_data_groups),
    url(r'^$', account.index),
]
