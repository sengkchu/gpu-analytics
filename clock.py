from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from gpu_scraper.py import run_all

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

sched = BlockingScheduler()

q = Queue(connection=conn)

def gpu_scraper_all():
    q.enqueue(run_all)


sched.add_job(gpu_scraper_all) #enqueue right away once
sched.add_job(gpu_scraper_all, 'interval', minutes=30)
sched.start()