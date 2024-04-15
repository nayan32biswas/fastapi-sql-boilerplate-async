from celery import shared_task


@shared_task
def ten_minute_crontab():
    print("tem_minute_crontab called")
    return True
