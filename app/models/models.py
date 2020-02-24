#!/bin/env python 2.7
# -*- coding: utf8 -*-

"""
Author: fured
Date: 2019.10.16
Desc: 数据库模型
"""

from django.db import models


class Hosts(models.Model):
    """
    主机表
    """
    host_name = models.CharField(max_length=100, null=True)
    ssh_host = models.CharField(max_length=100, null=True)
    ssh_user = models.CharField(max_length=100, null=True)
    ssh_port = models.CharField(max_length=100, null=True)
    os = models.CharField(max_length=100, null=True)
    group_name = models.CharField(max_length=100, null=True)
    commit = models.CharField(max_length=150, null=True)
    creattime = models.DateTimeField(auto_now_add=True)
    updatetime = models.DateTimeField(auto_now=True)
    is_deleted = models.IntegerField(default=0)

    class Meta:
        db_table = "hosts"


class Groups(models.Model):
    """
    主机组表
    """
    group_name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    detail = models.CharField(max_length=100, null=True, blank=True)
    is_deleted = models.IntegerField(default=0)

    class Meta:
        db_table = "groups"


class Package(models.Model):
    """
    代码包
    """
    package_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100, null=True)
    package_name = models.CharField(max_length=100, null=True, unique=True)
    date_str = models.CharField(max_length=10, null=True)
    is_deleted = models.IntegerField(default=0)
    md5 = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "packages"


class PlaybookFile(models.Model):
    """
    注册yml文件
    """
    playbook_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=100, null=True)
    # yml 文件所属项目
    project_name = models.CharField(max_length=100, null=True)
    # projects类型，
    project_type = models.CharField(max_length=100, null=True)
    # hosts组
    impact = models.CharField(max_length=100, null=True)
    author = models.CharField(max_length=100, null=True)
    register_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "playbooks"


class Tasks(models.Model):
    """
    任务表
    """
    STATUS = {
        (0, "PENDING"),
        (1, "STARTED"),
        (2, "COMPLETE"),
        (3, "FAILURE"),
        (4, "REVOKED"),
        (5, "NEW"),
    }
    TYPE = {
        ("host", "host"),
        ("group", "group")
    }
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100, null=True)
    task_set_id = models.IntegerField(null=True)
    playbook_id = models.IntegerField(null=True)
    package_id = models.IntegerField(null=True)
    inventory_type = models.CharField(max_length=30, null=True)
    inventory_id = models.IntegerField(null=True)
    exe_order = models.IntegerField(null=True)
    status = models.IntegerField(null=True, default=5, choices= STATUS)
    check_status = models.IntegerField(null=True, default=5, choices= STATUS)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tasks"


class TaskSet(models.Model):
    """
    任务集表
    """
    STATUS = {
        (0, "PENDING"),
        (1, "STARTED"),
        (2, "COMPLETE"),
        (3, "FAILURE"),
        (4, "REVOKED"),
        (5, "NEW"),
    }
    task_set_id =  models.AutoField(primary_key=True)
    task_set_name = models.CharField(max_length=100, null=True, unique=True)
    celery_id = models.CharField(max_length=150, null=True, blank=True)
    check_celery_id = models.CharField(max_length=150, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True, default=5, choices= STATUS)
    check_status = models.IntegerField(null=True, default=5, choices= STATUS)
    check_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = "task_set"

