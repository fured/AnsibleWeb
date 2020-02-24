#!/bin/env python 2.7
# -*- coding: utf-8 -*-

"""
Author: fured
Date: 2019.10.26
Desc: celery worker
"""

import commands
import logging as logger
import os

from app import settings
from app.models import models
from billiard.exceptions import Terminated
from celery import task
from datetime import datetime


@task(name="run-task-set", throw=(Terminated,))
def run_task_set(data):
    logger.info("Start run task set: %s, id: %d." % (data["task_set_name"],
        data["task_set_id"]))
    # 查询任务集并设定开始时间
    t_set = models.TaskSet.objects.get(task_set_id=data["task_set_id"])
    t_set.status = 1
    now_time = datetime.now()
    t_set.start_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    t_set.save()
    # 创建日志目录
    ansible_log_dir = "%s/%s" % (settings.ANSIBLE_LOG_DIR,
                                 now_time.strftime("%Y%m%d"))
    if not os.path.exists(ansible_log_dir):
        os.makedirs(ansible_log_dir)
    # 执行任务集中的任务
    for i in range(0, len(data["tasks"])):
        task = data["tasks"][i]
        logger.info("Start run task: %s, id: %d." %
                    (task["task_name"], task["task_id"]))
        
        t_obj = models.Tasks.objects.get(task_id=task["task_id"])
        t_obj.status = 1
        t_obj.save()

        ansible_log_file = "%s/ansible_%d_%d.log" % \
                           (ansible_log_dir, data["task_set_id"],
                            task["task_id"])

        bits = "cd %s;set -o pipefail;%s | tee -a %s" % \
               (settings.ANSIBLE_DIR, task["command"], ansible_log_file)
        logger.info(bits)
        (status, output) = commands.getstatusoutput("bash -c '%s'" % bits)
        if status != 0:
            t_obj.status = 3
            t_obj.save()
            for j in range(i+1, len(data["tasks"])):
                task_n = data["tasks"][j]
                t_obj = models.Tasks.objects.get(task_id=task_n["task_id"])
                t_obj.status = 4
                t_obj.save()
            logger.info("Status: %d." % status)
            t_set.status = 3
            t_set.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            t_set.save()
            logger.info("End run task set %d status %s." %
                        (data["task_set_id"], "FAILURE"))
            # 如果有执行失败的，不再继续往下执行
            raise Exception("Task execute failed.message: %s." % output)
        t_obj.status = 2
        t_obj.save()
        logger.info("status: %d." % status)
    t_set.status = 2
    t_set.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t_set.save()
    logger.info("End run task set %d status %s." %
                (data["task_set_id"], "COMPLETE"))


@task(name="check-task-set", throw=(Terminated,))
def check_task_set(data):
    logger.info("Start check task set: %s, id: %d." %
                (data["task_set_name"], data["task_set_id"]))
    t_set = models.TaskSet.objects.get(task_set_id=data["task_set_id"])
    t_set.check_status = 1
    now_time = datetime.now()
    t_set.check_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
    t_set.save()

    ansible_log_dir = "%s/%s" % (settings.ANSIBLE_LOG_DIR,
                                 now_time.strftime("%Y%m%d"))
    if not os.path.exists(ansible_log_dir):
        os.makedirs(ansible_log_dir)
    t_set_check_status = 2
    for i in range(0, len(data["tasks"])):
        task = data["tasks"][i]
        logger.info("Start check task: %s, id: %d." %
                    (task["task_name"], task["task_id"]))

        t_obj = models.Tasks.objects.get(task_id=task["task_id"])
        t_obj.check_status = 1
        t_obj.save()

        ansible_log_file = "%s/ansible_check_%d_%d.log" % \
                           (ansible_log_dir, data["task_set_id"],
                            task["task_id"])
        bits = "cd %s;set -o pipefail;%s --check| tee -a %s" % \
               (settings.ANSIBLE_DIR, task["command"], ansible_log_file)
        logger.info(bits)
        (status, output) = commands.getstatusoutput("bash -c '%s'" % bits)
        if status != 0:
            t_obj.check_status = 3
            t_obj.save()
            logger.info("Status: %d." % status)
            t_set_check_status = 3
        else:
            t_obj.check_status = 2
            t_obj.save()
            logger.info("status: %d." % status)
    if t_set_check_status == 2:
        t_set.check_status = 2
        t_set.save()
    if t_set_check_status == 3:
        t_set.check_status = 3
        t_set.save()
    logger.info("End check task set %d check status %d." %
                (data["task_set_id"], t_set_check_status))
