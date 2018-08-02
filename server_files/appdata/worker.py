import os
from gpu_scraper import run_all
import schedule
import time

def job():
    run_all()
    os.system("service apache2 reload")
    print("SCRAPE COMPLETE RELOADING SERVER")

schedule.every().day.at("00:10").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
