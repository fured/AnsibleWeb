#!/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Author: fured
Date: 20191024
Desc: yml 文件相关的api
"""

import logging as logger
import json
import os

from app.common.check import check_method
from app.models import models
from app import settings
from django.http.response import JsonResponse


@check_method("POST")
def register_yml(request):
    """
    注册playbook
    :param request:
    :return:
    """
    logger.debug("Start register yml file.")
    project_types = ["projects", "softs"]
    try:
        json_data = json.loads(request.body)
        file_name = json_data["file_name"]
        file_list = file_name.split(".")
        if len(file_list) != 2 or file_list[1] != "yml":
            raise Exception("file name is vaild.")
        project_name = json_data["project_name"]
        if project_name == "":
            raise Exception("project name is null.")
        project_type = json_data["project_type"]
        playbook_impact = json_data["playbook_impact"]
        author = json_data["author"]
        if project_type not in project_types:
            raise Exception("project type is vaild.")
    except Exception as error:
        logger.info(error.message)
        return JsonResponse({"code": 3001, "message": error.message})
    count = models.PlaybookFile.objects.filter(file_name=file_name,
                                               project_name=project_name,
                                               project_type=project_type).count()
    if count != 0:
        return JsonResponse({"code": 3002, "message": "file is existed."})
    file_path = "%s/playbooks/%s/%s/%s" % (settings.ANSIBLE_DIR, project_type,
                                           project_name, file_name)
    if not os.path.exists(file_path):
        return JsonResponse({
            "code": 3001,
            "message": "file not existed."
        })
    item = models.PlaybookFile(file_name=file_name, project_name=project_name,
                               project_type=project_type,
                               impact=playbook_impact, author=author)
    item.save()
    response = {"code": 0, "message": "success"}
    return JsonResponse(response)


@check_method("POST")
def get_data_all(requests):
    """
    获取所有有效的playbook文件
    :param requests:
    :return:
    """
    logger.debug("Start obtain all playbook data.")
    data = json.loads(requests.body)
    limit = data["limit"]
    offset = data["offset"]
    all_play = models.PlaybookFile.objects.all()\
            .order_by("project_type", "project_name")[offset:offset+limit]
    total = models.PlaybookFile.objects.all().count()
    rows = []
    for item in all_play:
        rows.append({
            "playbook_id": item.playbook_id,
            "project_type": item.project_type,
            "project_name": item.project_name,
            "file_name": item.file_name,
            "playbook_impact": item.impact,
            "author": item.author,
            "register_time": item.register_time
        })
    return JsonResponse({
        "code": 0,
        "message": "success",
        "total": total,
        "rows": rows
    })


@check_method("POST")
def get_data_ymldetail(requests):
    """
    获取playbook文件详情
    :param requests:
    :return:
    """
    logger.debug("Start obtain playbook detail.")
    data = json.loads(requests.body)
    playbook_id = data["playbook_id"]
    playbook = models.PlaybookFile.objects.get(playbook_id=playbook_id)
    file_path = "%s/playbooks/%s/%s/%s" % (settings.ANSIBLE_DIR, 
            playbook.project_type, playbook.project_name, playbook.file_name)
    try:
        with open(file_path, "r") as fb:
            content = fb.read()
    except IOError as error:
        logger.info("Get yml detail fail:%s" % error.message)
        return JsonResponse({
            "code": 3003,
            "message": error.message
        })

    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": {
            "content": content
        }
    })


@check_method("GET")
def get_data_groups(requests):
    """
    获取所有主机组信息
    :param requests:
    :return:
    """
    logger.debug("Start obtain groups data.")
    groups = models.Groups.objects.filter(is_deleted=0)
    group_s = []
    for item in groups:
        group_s.append({"group_id": item.id, "group_name": item.group_name})

    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": {
            "groups": group_s    
        }
    })
