#!/bin/env python 2.7
# -*- coding: utf-8 -*-

"""
Author: fured
Date: 2019.10.16
Desc: 主机管理中心相关view
"""

import json
import logging as logger


from app import settings
from app.common.check import  check_method
from app.models.inventory import get_all_host_info
from app.models.inventory import get_parent_g
from app.models import models
from app.common.f_configparser import FConfigParser
from django.http import JsonResponse


@check_method("GET")
def gen_host_file(request):
    """
    按照数据库中主机信息，生成ansible主机文件
    :param request:
    :return:
    """
    logger.debug("Start again generate host file.")
    # get all hosts info
    info_h = get_all_host_info()
    # generate hots file
    try:
        config_h = FConfigParser()
        for group in info_h:
            config_h.add_section(group["group"])
            for item in group["items"]:
                name = item["host_name"]
                ssh_host = item["ssh_host"]
                ssh_user = item["ssh_user"]
                ssh_port = item["ssh_port"]
                build = "ansible_ssh_host={:<15} ansible_ssh_user={:<8} " \
                        "ansible_ssh_port={}".format(ssh_host, ssh_user,
                                                     ssh_port)
                config_h.set(group["group"], "{:20}".format(name), build)
        host_file = settings.HOSTS_FILE["path"] + \
            settings.HOSTS_FILE["file_name"]
        with open(host_file, "w") as configfile:
            config_h.write(configfile)
    except Exception as error:
        response = {"code": 2100, "message": error.message}
    else:
        response = {"code": 0, "message": "success"}
    return JsonResponse(response)


@check_method("GET")
def gen_group_file(request):
    """
    按照数据库中主机组包含关系，生产ansible主机组文件
    :param request:
    :return:
    """
    logger.debug("Start again generate group file.")
    # get group info
    info_g = get_parent_g()
    logger.debug(info_g)
    try:
        config_g = FConfigParser()
        for p_group in info_g:
            group_name = "%s:children" % p_group["g_group"]
            config_g.add_section(group_name)
            for item in p_group["children"]:
                logger.debug(item)
                config_g.set(group_name, item, "")
        group_file = settings.GROUPS_FILE["path"] +\
            settings.GROUPS_FILE["file_name"]
        with open(group_file, "w") as configfile:
            config_g.write(configfile)
    except Exception as error:
        response = {"code": 2100, "message": error.message}
    else:
        response = {"code": 0, "message": "success"}
    return JsonResponse(response)


@check_method("POST")
def add_host(requests):
    """
    增加Ansible主机
    :param requests:
    :return:
    """
    logger.debug("Start add host.")
    data = json.loads(requests.body)
    # 主机名不能和已有主机、已有主机组重复
    if models.Hosts.objects.filter(is_deleted=0, host_name=data["host_name"])\
            .count() != 0 or models.Groups.objects.filter(is_deleted=0,
            group_name=data["host_name"]).count() != 0:
        print models.Hosts.objects.filter(is_deleted=0, host_name=data["host_name"]).count()
        print models.Groups.objects.filter(is_deleted=0,group_name=data["host_name"]).count()
        return  JsonResponse({
            "code": 2004,
            "message": "host name is existed! please rename!"
        })
    # 新主机所属的主机组不能是已存在的父主机组
    if models.Groups.objects.filter(is_deleted=0, 
            group_name=data["host_group"], type="parent").count() != 0:
        print data["host_group"]
        return JsonResponse({
            "code": 2005,
            "message": "group name is existed as parent group! please rename."
        })
    # 新主机组名 不能和已有主机重名
    if models.Hosts.objects.filter(is_deleted=0, host_name=data["host_group"])\
            .count() != 0:
        return JsonResponse({
            "code": 2006,
            "message": "group name is existed as host! please rename."
        })
    # 如果主机组不存在则新建主机组
    if models.Groups.objects.filter(is_deleted=0, 
            group_name=data["host_group"]).count() == 0:
        models.Groups(group_name=data["host_group"], type="children").save()
    models.Hosts(host_name=data["host_name"], ssh_host=data["host_ip"], 
            ssh_port=data["host_port"], ssh_user=data["host_user"], 
            os=data["host_os"], group_name=data["host_group"], 
            commit=data["host_note"]).save()
    logger.info("Add host:%s." % data["host_name"])
    return JsonResponse({
        "code": 0,
        "message": "success"
    })


@check_method("POST")
def add_group(requests):
    """
    增加主机组
    :param requests:
    :return:
    """
    logger.debug("Start add parent group.")
    data = json.loads(requests.body)
    group_name = data["group_name"]
    c_groups = data["child_group"]
    # 主机组名不能和已有主机、已有主机组重复
    if models.Hosts.objects.filter(is_deleted=0, host_name=group_name).\
            count() !=0 or models.Groups.objects.filter(is_deleted=0, 
            group_name=group_name).count() != 0:
        return JsonResponse({
            "code": 2007,
            "message": "group name is existed as host or group."
        })
    childrens = []
    for item in c_groups:
        childrens.append(models.Groups.objects.get(id=int(item)).group_name)
    detail = json.dumps({"children": childrens})
    models.Groups(group_name=group_name, type="parent", detail=detail).save()
    logger.info("Add group: %s." % group_name)
    return JsonResponse({
        "code": 0,
        "message": "success"
    })


@check_method("GET")
def get_data_childgroup(requests):
    """
    获取所有有效的孩子主机组
    :param requests:
    :return:
    """
    logger.debug("Start obtain children group data.")
    c_groups = models.Groups.objects.filter(is_deleted=0, type="children")
    c_groups_r = []
    for item in c_groups:
        c_groups_r.append({
            "group_id": item.id,
            "group_name": item.group_name
        })
    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": c_groups_r
    })


@check_method("POST")
def get_data_group(requests):
    """
    获取所有主机组信息
    :param requests:
    :return:
    """
    logger.debug('Start obtin all group data.')
    limit = json.loads(requests.body)["limit"]
    offset = json.loads(requests.body)["offset"]
    groups = models.Groups.objects.filter(is_deleted=0)[offset:offset+limit]
    group_d = []
    for item in groups:
        group_d.append({
            "group_id": item.id,
            "group_name": item.group_name,
            "group_type": item.type
        })
    total =  models.Groups.objects.all().count()
    return JsonResponse({
        "code": 0,
        "message": "success",
        "total": total,
        "rows": group_d
    })


@check_method("GET")
def get_data_host(requests):
    """
    获取所有主机信息
    :param requests:
    :return:
    """
    logger.debug("Start obtion host info for group.")
    group_name = requests.GET['group_name']
    group_type = requests.GET['group_type']
    if group_type == "children":
        hosts = models.Hosts.objects.filter(is_deleted=0, group_name=group_name)
    elif group_type == "parent":
        ch_groups = models.Groups.objects.get(group_name=group_name)
        childs = json.loads(ch_groups.detail)["children"]
        hosts = []
        for child in childs:
            c_hosts = models.Hosts.objects.filter(is_deleted=0, group_name=child)
            hosts.extend(c_hosts)
    else:
        return JsonResponse({
            "code": 2001,
            "message": "group type is valid."
        })
    hosts_d = []
    for host in hosts:
        hosts_d.append({
            "host_id": host.id,
            "host_name": host.host_name,
            "host_ip": host.ssh_host,
            "host_user": host.ssh_user,
            "host_port": host.ssh_port,
            "host_os": host.os,
            "host_group_name": host.group_name
        })
    return JsonResponse({
        "code": 0,
        "message": "success",
        "rows": hosts_d
    })


@check_method("POST")
def delete_inventory(requests):
    """
    删除主机、子主机组、父主机组
    :param requests:
    :return:
    """
    logger.debug("Start delete inventory.")
    d_type = json.loads(requests.body)["type"]
    d_id = json.loads(requests.body)["id"]
    try:
        if d_type == "host":
            if models.Hosts.objects.filter(id=d_id,is_deleted=0).count() != 1:
                raise("Host not exist.")
            models.Hosts.objects.filter(id=d_id).update(is_deleted=1)
            logger.info("Deleted host: %d." % d_id)

        elif d_type == "children":
            group = models.Groups.objects.filter(id=d_id, type="children",
                                                 is_deleted=0)
            g_name = group[0].group_name
            if group.count() != 1:
                raise("Children group not exist.")
            group.update(is_deleted=1)
            logger.info("Delete child group:%s." % g_name)

            hosts = models.Hosts.objects.filter(group_name=g_name,
                                                is_deleted=0)
            for host in hosts:
                models.Hosts.objects.filter(id=host.id).update(is_deleted=1)
                logger.info("Delete host: %s." % host.host_name)

            parents = models.Groups.objects.filter(type="parent")
            for parent in parents:
                detail = json.loads(parent.detail)
                if g_name in detail["children"]:
                    detail["children"].remove(g_name)
                models.Groups.objects.filter\
                    (id=parent.id).update(detail=json.dumps(detail))

        elif d_type == "parent":
            if models.Groups.objects.filter(id=d_id, type="parent",
                                            is_deleted=0).count() != 1:
                raise("Parent group not exist.")
            models.Groups.objects.filter(id=d_id, type="parent",
                                         is_deleted=0).update(is_deleted=1)
            logger.info("Delete parent group: %d." % d_id)
        else:
            return JsonResponse({
                "code": 2002, 
                "message": "delete type nor existed."
            })
        return JsonResponse({
            "code": 0,
            "message": "success"
        })
    except Exception as error:
        return JsonResponse({
            "code": 2003,
            "message": error.message
        })
