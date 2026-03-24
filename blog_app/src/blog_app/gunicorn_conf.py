bind = f"0.0.0.0:8000"

# Кол-во worker процессов
workers = 2

# Класс worker процесса.
worker_class = "uvicorn.workers.UvicornWorker"

# Worker timeout (секунды), должно быть синхронизированно с nginx.
timeout = 30

# Graceful timeout (секунды)
graceful_timeout = 60

# Максимальное кол-во запросов, которое обработает worker
# перед перезапуском.
max_requests = 1000
max_requests_jitter = 5

# "-" - вывод в stdout (удобно для Docker)
accesslog = "-"

errorlog = "-"

loglevel = "info"

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(T)s'


# Ограничение размера заголовков запроса (bytes)
# Защита от DoS атак с огромными заголовками

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

proc_name = "gunicorn_fastapi"

def on_starting(server):  # new *
    """
    Вызывается перед запуском master процесса
    Полезно для инициализации shared resources
    """
    server.log.info("Gunicorn master starting")


def on_reload(server):  # new *
    """
    Вызывается при reload конфигурации
    """
    server.log.info("Gunicorn reloading")

def when_ready(server):  # new *
    """
    Вызывается когда сервер готов принимать запросы
    Полезно для health checks
    """
    server.log.info("Gunicorn is ready. Spawning workers")


def pre_fork(server, worker):  # new *
    """
    Вызывается перед fork worker процесса
    """
    pass


def post_fork(server, worker):  # new *
    """
    Вызывается после fork worker процесса
    Полезно для инициализации per-worker ресурсов (DB connections, etc.)
    """
    server.log.info(f"Worker spawned (pid: {worker.pid})")


def pre_exec(server):  # new *
    """
    Вызывается перед новым exec при reload
    """
    server.log.info("Forked child, re-executing.")


def worker_int(worker):  # new *
    """
    Вызывается когда worker получает SIGINT или SIGQUIT
    """
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")


def worker_abort(worker):  # new *
    """
    Вызывается когда worker получает SIGABRT (обычно при timeout)
    """
    worker.log.warning(f"Worker received SIGABRT signal (pid: {worker.pid})")