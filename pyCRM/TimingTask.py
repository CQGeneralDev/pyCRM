# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@Module Name: TimingTask
@Author: gao
@Contact: gwj337536127@163.com
@Create date: 2018/9/3 9:52
@Description:定时任务
-------------------------------------------------
@Change Activity:
    2018/9/3:创建文件
-------------------------------------------------
"""
__author__ = 'gao'

import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from pyCRM import task_data_conn

tz = pytz.timezone('Asia/Shanghai')

jobstores = {
    'default': SQLAlchemyJobStore(engine=task_data_conn)
}
executors = {
    'default': ThreadPoolExecutor(200),
    'processpool': ProcessPoolExecutor(10)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 1,
    'misfire_grace_time': 60
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=jobstores, timezone=tz)

if __name__ != '__main__':
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
