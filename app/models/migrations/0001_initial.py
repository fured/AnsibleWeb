# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.CharField(max_length=100, null=True)),
                ('type', models.CharField(max_length=100, null=True)),
                ('detail', models.CharField(max_length=100, null=True, blank=True)),
                ('is_deleted', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'groups',
            },
        ),
        migrations.CreateModel(
            name='Hosts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host_name', models.CharField(max_length=100, null=True)),
                ('ssh_host', models.CharField(max_length=100, null=True)),
                ('ssh_user', models.CharField(max_length=100, null=True)),
                ('ssh_port', models.CharField(max_length=100, null=True)),
                ('os', models.CharField(max_length=100, null=True)),
                ('group_name', models.CharField(max_length=100, null=True)),
                ('commit', models.CharField(max_length=150, null=True)),
                ('creattime', models.DateTimeField(auto_now_add=True)),
                ('updatetime', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'hosts',
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('package_id', models.AutoField(serialize=False, primary_key=True)),
                ('project_name', models.CharField(max_length=100, null=True)),
                ('package_name', models.CharField(max_length=100, unique=True, null=True)),
                ('date_str', models.CharField(max_length=10, null=True)),
                ('is_deleted', models.IntegerField(default=0)),
                ('md5', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'packages',
            },
        ),
        migrations.CreateModel(
            name='PlaybookFile',
            fields=[
                ('playbook_id', models.AutoField(serialize=False, primary_key=True)),
                ('file_name', models.CharField(max_length=100, null=True)),
                ('project_name', models.CharField(max_length=100, null=True)),
                ('project_type', models.CharField(max_length=100, null=True)),
                ('impact', models.CharField(max_length=100, null=True)),
                ('author', models.CharField(max_length=100, null=True)),
                ('register_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'playbooks',
            },
        ),
        migrations.CreateModel(
            name='Tasks',
            fields=[
                ('task_id', models.AutoField(serialize=False, primary_key=True)),
                ('task_name', models.CharField(max_length=100, null=True)),
                ('task_set_id', models.IntegerField(null=True)),
                ('playbook_id', models.IntegerField(null=True)),
                ('package_id', models.IntegerField(null=True)),
                ('inventory_type', models.CharField(max_length=30, null=True)),
                ('inventory_id', models.IntegerField(null=True)),
                ('exe_order', models.IntegerField(null=True)),
                ('status', models.IntegerField(default=5, null=True, choices=[(4, b'REVOKED'), (5, b'NEW'), (1, b'STARTED'), (0, b'PENDING'), (2, b'COMPLETE'), (3, b'FAILURE')])),
                ('check_status', models.IntegerField(default=5, null=True, choices=[(4, b'REVOKED'), (5, b'NEW'), (1, b'STARTED'), (0, b'PENDING'), (2, b'COMPLETE'), (3, b'FAILURE')])),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tasks',
            },
        ),
        migrations.CreateModel(
            name='TaskSet',
            fields=[
                ('task_set_id', models.AutoField(serialize=False, primary_key=True)),
                ('task_set_name', models.CharField(max_length=100, unique=True, null=True)),
                ('celery_id', models.CharField(max_length=150, null=True, blank=True)),
                ('check_celery_id', models.CharField(max_length=150, null=True, blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=5, null=True, choices=[(4, b'REVOKED'), (5, b'NEW'), (1, b'STARTED'), (0, b'PENDING'), (2, b'COMPLETE'), (3, b'FAILURE')])),
                ('check_status', models.IntegerField(default=5, null=True, choices=[(4, b'REVOKED'), (5, b'NEW'), (1, b'STARTED'), (0, b'PENDING'), (2, b'COMPLETE'), (3, b'FAILURE')])),
                ('check_time', models.DateTimeField(null=True, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'task_set',
            },
        ),
    ]
