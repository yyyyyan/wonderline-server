bind = "0.0.0.0:8000"
workers = 1
accesslog = "-"  # STDOUT
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "debug"
capture_output = True
