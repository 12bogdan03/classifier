import multiprocessing


bind = "0.0.0.0:8000"
accesslog = '-'  # log to stdout
loglevel = 'info'
workers = multiprocessing.cpu_count() * 2
graceful_timeout = 60
timeout = 90
