import multiprocessing

bind = "127.0.0.1:8081"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/var/tmp/askme.gunicorn.log'
