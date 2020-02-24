#!/bin/ens python2.7
# -*- coding: utf-8 -*-

"""
Author: fured
Date: 2019.10.17
Desc: 主机管理中心相关model处理
"""

import json
import itertools
import logging as logger

from models import Hosts
from models import Groups


def get_all_host_info():
    vaild_hosts = Hosts.objects.filter(is_deleted=0)\
        .values("host_name", "ssh_host", "ssh_user", "ssh_port", "group_name")
    hosts_data = [{"group": group_name, "items": list(items)}
        for group_name, items in itertools.groupby(vaild_hosts,
            lambda x: x["group_name"])
    ]
    return hosts_data


def get_parent_g():
    parent_g = Groups.objects.filter(is_deleted=0, type="parent")\
        .values("group_name", "detail")
    logger.debug(parent_g)
    group_data = []
    for item in parent_g:
        i = {
            "g_group": item["group_name"],
            "children": json.loads(item["detail"])["children"]
        }
        group_data.append(i)
    return group_data
