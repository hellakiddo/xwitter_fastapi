from celery import Celery
from auth.send_email import send_confirmation_email

app = Celery('xwitter')
app.conf.broker_url = 'redis://redis:6379'
app.conf.result_backend = 'redis://redis:6379'

app.autodiscover_tasks()
@app.task
def send_confirm_email_task(email, code):
    send_confirmation_email(email, code)
