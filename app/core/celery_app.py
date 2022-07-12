from celery import Celery

celery_app = Celery("worker", broker="ampq://guest@queue//")

celery_app.conf.task_routes = {"worker.test_task": "main-queue"}
