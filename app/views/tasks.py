#!/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Author:fured
Date: 20191019
Desc: 任务相关view
"""

import commands
import json
import logging as logger
import os

from app import settings
from app.common.check import check_method
from app.models.models import Package
from app.models import models
from app import settings
from app.tasks import run_task_set
from app.tasks import check_task_set
from billiard.exceptions import Terminated
from celery.task.control import revoke
from celery.result import AsyncResult
from datetime import datetime
from datetime import timedelta
from django.http.response import JsonResponse


@check_method("GET")
def update_package(requests):
    """
    更新代码包到数据库
    :param requests:
    :return:
    """
    logger.debug("Start update package for databases.")
    package_root_dir = settings.PACKAGE_ROOT_DIR
    for root, dirs, files in os.walk(package_root_dir):
        for file in files:
            package_name = file
            path_list = root.split("/")
            if not package_name.endswith(".tar.gz") and \
                    not package_name.endswith(".zip"):
                continue
            result = Package.objects.filter(package_name=file)
            if len(result) == 0:
                items = Package(project_name=path_list[2], package_name=file,
                                date_str=path_list[3])
                items.save()
    return JsonResponse({"code": 0, "message": "success"})


@check_method("POST")
def get_all_data(requests):
    """
    获取所有新增任务集需要的信息
    :param requests:
    :return:
    """
    logger.debug("Start get all data for add taskset.")
    dict_data = json.loads(requests.body)
    time_range = dict_data["range"]
    
    playbooks = models.PlaybookFile.objects.all().order_by("project_type",
                                                           "project_name")
    pb_data = []
    for item in playbooks:
        pb_data.append({
            "playbook_id": item.playbook_id,
            "pb_type": item.project_type,
            "pb_project_name": item.project_name,
            "pb_file_name": item.file_name
        })

    if time_range not in ["5", "10", "30", "all"]:
        return JsonResponse({"code": 1002, "message": "time range is error."})
    elif time_range == "all":
        packages = models.Package.objects.filter(is_deleted=0).\
            orderby("project_name")
    else:
        date_str_range = (datetime.now() -
                          timedelta(days=int(time_range))).strftime("%Y%m%d")
        sql = """select * from packages where is_deleted=0 and date_str >= %s 
               order by project_name,date_str""" % date_str_range
        packages = models.Package.objects.raw(sql)
    pg_data = []
    for item in packages:
        pg_data.append({
            "package_id": item.package_id,
            "pg_file_name": "%s/%s/%s" % (item.project_name, item.date_str,
                                          item.package_name)
        })

    hosts = models.Hosts.objects.filter(is_deleted=0)
    h_data = []
    for item in hosts:
        h_data.append({
            "host_id": item.id,
            "host_name": "%s-%s" % (item.host_name, item.ssh_host)
        })

    groups = models.Groups.objects.filter(is_deleted=0)
    g_data = []
    for item in groups:
        g_data.append({
            "group_id": item.id,
            "group_name": item.group_name
        })

    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": {
            "playbook": pb_data,
            "package": pg_data,
            "inventory": {
                "host": h_data,
                "group": g_data
            }
        }
    })


@check_method("POST")
def get_taskset_data(requests):
    """
    获取任务集信息
    :param requests: 
    :return: 
    """
    logger.debug("Start obtain task set data.")
    data = requests.body
    dict_data = json.loads(data)
    offset = dict_data["offset"]
    limit = dict_data["limit"]
    t_sets = models.TaskSet.objects.all().\
                 order_by("-task_set_id")[offset:offset+limit]
    total = models.TaskSet.objects.all().count()
    rows = []
    for t_set in t_sets:
        rows.append({
            "taskset_id": t_set.task_set_id,
            "taskset_name": t_set.task_set_name,
            "taskset_cid": t_set.celery_id,
            "taskset_c_cid": t_set.check_celery_id,
            "taskset_status": settings.TASK_STATUS[t_set.status],
            "check_status": settings.TASK_STATUS[t_set.check_status]
        })
    return JsonResponse({
        "code": 0,
        "message": "success",
        "total": total,
        "totalNotFiltered": total,
        "rows": rows
    })


@check_method("GET")
def get_tasks_data(requests):
    """
    获取任务集中的任务信息
    :param requests: 
    :return: 
    """
    logger.debug("Start obtain tasks data.")
    t_set_id = int(requests.GET["task_set_id"])
    logger.info("task set id: %d." % t_set_id)
    tasks = models.Tasks.objects.filter(task_set_id=t_set_id)
    rows = []
    for task in tasks:
        playbook = models.PlaybookFile.objects.get(playbook_id=task.playbook_id)
        package = models.Package.objects.get(package_id=task.package_id)
        if task.inventory_type == "host":
            inventory = models.Hosts.objects.get(id=task.inventory_id).host_name
        if task.inventory_type == "group":
            inventory = models.Groups.objects.get(id=task.inventory_id).group_name
        rows.append({
            "task_id": task.task_id,
            "task_set_id": t_set_id,
            "playbook": "%s/%s/%s" % (playbook.project_type, 
                                      playbook.project_name, 
                                      playbook.file_name),
            "package": "%s/%s/%s" % (package.project_name, package.date_str,
                                     package.package_name),
            "inventory_type": task.inventory_type,
            "inventory": inventory,
            "task_status": settings.TASK_STATUS[task.status],
            "check_status": settings.TASK_STATUS[task.check_status]
        })
    return JsonResponse({
        "code": 0,
        "message": "success",
        "rows": rows
    })


@check_method("POST")
def payload_task_set(requests):
    """
    新增任务集
    :param requests: 
    :return: 
    """
    logger.debug("Start payload task set.")
    data = requests.body
    dict_data = json.loads(data)
    # 为了保证task执行顺序，对json中的任务进行插入排序
    task_set_name = dict_data["task_set_name"]
    if models.TaskSet.objects.filter(task_set_name=task_set_name).count() != 0:
        return JsonResponse({
            "code": 1004,
            "message": "task set name is existed"
        })
    tasks = dict_data["tasks"]
    for i in range(1, len(tasks)):
        item = tasks[i]["exe_order"]
        key = tasks[i]
        j = i - 1
        while j >= 0 and item < tasks[j]["exe_order"]:
            tasks[j+1] = tasks[j]
            j = j - 1
        tasks[j+1] = key
    # 入库
    task_set = models.TaskSet(task_set_name=task_set_name)
    task_set.save()
    task_set_id = task_set.task_set_id
    logger.info("Add task set:%s, id:%d." % (task_set_name, task_set_id))
    for i in range(0, len(tasks)):
        item = tasks[i]
        task = models.Tasks(task_name=item["task_name"], 
                task_set_id=task_set_id, playbook_id=item["playbook_id"],
                package_id=item["package_id"], 
                inventory_type=item["inventory"]["type"],
                inventory_id=item["inventory"]["id"],
                exe_order=item["exe_order"])
        task.save()
    return JsonResponse({
        "code": 0,
        "message": "success"
    })


@check_method("POST")
def run_check_task_set(requests):
    """
    运行任务集
    :param requests:
    :return:
    """
    logger.debug("Start run task set.")
    data = requests.body
    dict_data = json.loads(data)
    run_type = dict_data["type"]
    t_set_id = dict_data["task_set_id"]
    tasks = models.Tasks.objects.filter(task_set_id=t_set_id).order_by("exe_order")
    tasks_ = []
    for task in tasks:
        tasks_.append({
            "task_id": task.task_id,
            "task_name": task.task_name,
            "playbook_id": task.playbook_id,
            "package_id": task.package_id,
            "inventory": {
                "type": task.inventory_type,
                "id": task.inventory_id
            }
        })
    # 组装任务
    celery_tasks = task_factory(tasks_)
    
    # producer
    task_set = models.TaskSet.objects.get(task_set_id=t_set_id)
    c_data = {
        "task_set_name": task_set.task_set_name,
        "task_set_id": t_set_id,
        "tasks": celery_tasks
    }
    if run_type == "run":
        s1 = run_task_set.s(c_data)
        res = s1.delay()
        task_set.celery_id = res.task_id
        task_set.status = 0
        task_set.save()
        for task in tasks:
            task.status = 0
            task.save()
    elif run_type == "check":
        s1 = check_task_set.s(c_data)
        res = s1.delay()
        task_set.check_celery_id = res.task_id
        task_set.check_status = 0
        task_set.save()
        for task in tasks:
            task.check_status = 0
            task.save()
    return JsonResponse({
        "code": 0,
        "message": "success.",
        "data": {
            "celery_id": res.task_id,
            "type": run_type,
            "status": settings.TASK_STATUS[0]
        }
    })


@check_method("POST")
def task_set_status(requests):
    """
    获取任务集当前状态
    :param requests:
    :return:
    """
    logger.debug("Start get task set run status.")
    data = requests.body
    dict_data = json.loads(data)
    celery_id = dict_data["celery_id"]
    run_type = dict_data["type"]
    if run_type == "run":
        t_set = models.TaskSet.objects.get(celery_id=celery_id)
        t_set_status = {
            "tast_set": t_set.task_set_id,
            "status": settings.TASK_STATUS[t_set.status]
        }

        t_objs_status = []
        t_objs = models.Tasks.objects.filter(task_set_id=t_set.task_set_id)
        for t_obj in t_objs:
            t_objs_status.append({
                "task_id": t_obj.task_id, 
                "status": settings.TASK_STATUS[t_obj.status]
            })
        logger.info("Task set id: %s, current run: %s." %
                    (t_set.task_set_id, t_set.status))
    elif run_type == "check":
        t_set = models.TaskSet.objects.get(check_celery_id=celery_id)
        t_set_status = {
            "tast_set": t_set.task_set_id,
            "status": settings.TASK_STATUS[t_set.check_status]
        }
        t_objs_status = []
        t_objs = models.Tasks.objects.filter(task_set_id=t_set.task_set_id)
        for t_obj in t_objs:
            t_objs_status.append({
                "task_id": t_obj.task_id,
                "status": settings.TASK_STATUS[t_obj.check_status]
            })
        logger.info("Task set id: %s, current run: %s." %
                    (t_set.task_set_id, t_set.check_status))

    return JsonResponse({
        "code": 0,
        "message": "success.",
        "data": {
            "task_set": t_set_status,
            "tasks": t_objs_status
        }
    })


@check_method("POST")
def get_task_log(requests):
    """
    获取运行任务执行日志
    :param requests:
    :return:
    """
    logger.debug("Start get task ansible log.")
    data = requests.body
    dict_data = json.loads(data)
    s_line = dict_data["seek"]
    t_set_id = dict_data["task_set_id"]
    t_obj_id = dict_data["task_id"]

    t_set = models.TaskSet.objects.get(task_set_id=t_set_id)
    t_obj = models.Tasks.objects.get(task_id=t_obj_id)

    if t_set.status == 0 or t_obj.status == 0:
        logger.info("Task set %d or task %d not run." % (t_set_id, t_obj_id))
        return JsonResponse({"code": 1001, "message": "Not run."})
    
    ansible_log_file = "%s/%s/ansible_%d_%d.log" % \
                       (settings.ANSIBLE_LOG_DIR,
                        t_set.start_time.strftime("%Y%m%d"),
                        t_set_id, t_obj_id)
    if not os.path.exists(ansible_log_file):
        logger.info("Log file not exist: %s." % ansible_log_file)
        return JsonResponse({"code": 1001, "message": "Log file not exist."})
    
    with open(ansible_log_file, "r") as fb:
        fb.seek(s_line)
        log_data = fb.read()
        new_seek = fb.tell()
    if t_obj.status in [2, 3, 4]:
        read_flag = False
    else:
        read_flag = True

    return JsonResponse({
        "code": 0,
        "message": "success.",
        "data": {
            "new_seek": new_seek,
            "read_flag": read_flag,
            "log": log_data
        }
    })


@check_method("POST")
def get_check_log(requests):
    """
    获取检查任务执行日志
    :param requests:
    :return:
    """
    logger.debug("Start get task check ansible log.")
    data = requests.body
    dict_data = json.loads(data)
    s_line = dict_data["seek"]
    t_set_id = dict_data["task_set_id"]
    t_obj_id = dict_data["task_id"]
    t_set = models.TaskSet.objects.get(task_set_id=t_set_id)
    t_obj = models.Tasks.objects.get(task_id=t_obj_id)
    if t_set.check_status == 0 or t_obj.check_status == 0:
        logger.info("Task set %d or task %d not check." % (t_set_id, t_obj_id))
        return JsonResponse({"code": 1001, "message": "Not run."})

    ansible_log_file = "%s/%s/ansible_check_%d_%d.log" % \
                       (settings.ANSIBLE_LOG_DIR,
                        t_set.check_time.strftime("%Y%m%d"),
                        t_set_id, t_obj_id)
    if not os.path.exists(ansible_log_file):
        logger.info("Log file not exist: %s." % ansible_log_file)
        return JsonResponse({"code": 1001, "message": "Log file not exist."})
    with open(ansible_log_file, "r") as fb:
        fb.seek(s_line)
        log_data = fb.read()
        new_seek = fb.tell()
    if t_obj.check_status in [2, 3, 4]:
        read_flag = False
    else:
        read_flag = True
    return JsonResponse({
        "code": 0,
        "message": "success.",
        "data": {
            "new_seek": new_seek,
            "read_flag": read_flag,
            "log": log_data
        }
    })


@check_method("POST")
def task_set_revoke(requests):
    """
    取消或者中止正在运行的任务
    :param requests:
    :return:
    """
    logger.debug("Start revoke task set.")
    data = requests.body
    dict_data = json.loads(data)
    task_celery_id = dict_data["celery_id"]
    run_type= dict_data["type"]
    now_status = AsyncResult(task_celery_id).status
    if now_status in ["SUCCESS", "FAILURE", "REVOKED"]:
        logger.info("Task set: %s is over." % task_celery_id)
        return JsonResponse({"code": 1002, "message": "Already over"})
    revoke(task_celery_id, terminate=True, singal="SIGKILL")

    if run_type == "run":
        t_set = models.TaskSet.objects.get(celery_id=task_celery_id)
        t_set.status = 4
        if now_status == "PENDING":
            t_set.start_time = t_set.end_time = datetime.now().\
                strftime("%Y-%m-%d %H:%M:%S")
        else:
            t_set.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t_set.save()

        t_objs = models.Tasks.objects.filter(task_set_id=t_set.task_set_id)
        for t_obj in t_objs:
            if t_obj.status not in [2, 3, 4]:
                t_obj.status = 4
                t_obj.save()
    if run_type == "check":
        t_set = models.TaskSet.objects.get(check_celery_id=task_celery_id)
        t_set.check_status = 4
        t_set.save()
        t_objs = models.Tasks.objects.filter(task_set_id=t_set.task_set_id)
        for t_obj in t_objs:
            if t_obj.status not in [2, 3, 4]:
                t_obj.check_status = 4
                t_obj.save()

    logger.info("Task set %s is revoke." % task_celery_id)
    return JsonResponse({"code": 0, "message": "success."})


def task_factory(data):
    """
    任务工厂，用于组装任务
    :param data:
    :return:
    """
    celery_task = []
    for task in data:
        playbook = models.PlaybookFile.objects.get(playbook_id=
                task["playbook_id"])
        yml = "%s/%s/%s/%s" % (settings.PLAYBOOK_DIR, playbook.project_type,
                               playbook.project_name, playbook.file_name)

        package = models.Package.objects.get(package_id=task["package_id"])
        pack_path = "%s/%s/%s/%s" % (settings.PACKAGE_ROOT_DIR,
                                     package.project_name, package.date_str,
                                     package.package_name)

        if task["inventory"]["type"] == "host":
            inventory = models.Hosts.objects.get(id=task["inventory"]["id"])
            limit_host = inventory.host_name
        if task["inventory"]["type"] == "group":
            inventory = models.Groups.objects.get(id=task["inventory"]["id"])
            limit_host = inventory.group_name

        command = "ansible-playbook %s -e PACKAGE=%s --limit %s" % \
                  (yml, pack_path, limit_host)
        celery_task.append({
            "task_id": task["task_id"],
            "task_name": task["task_name"], 
            "command": command
        })
    return celery_task
