import atexit
import fcntl
import logging

from guniflask.scheduling import scheduled

log = logging.getLogger(__name__)


def unique_scheduled_v1(func):
    def wrap_func(*args, **kwargs):
        lock_file_name = func.__name__.upper() + ".LOCK"
        lock_file = open(lock_file_name, "wb")

        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            log.debug(f"Locking scheduled {func.__name__}")
            func(*args, **kwargs)
        except:
            log.warning(f"File locked cannot execute the func {func.__name__}")

        def unlock():
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()

        atexit.register(unlock)

    return wrap_func


def unique_scheduled_v2(cron: str = None, interval: int = None, initial_delay: int = None):
    def decorator(func):
        @scheduled(cron, interval, initial_delay)
        def wrap_func(*args, **kwargs):
            lock_file_name = func.__name__.upper() + ".LOCK"
            lock_file = open(lock_file_name, "wb")

            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                print("Locked!")
                func(*args, **kwargs)
            except:
                log.warning(f"File locked cannot execute the func {func.__name__}")

            def unlock():
                fcntl.flock(lock_file, fcntl.LOCK_UN)
                lock_file.close()

            atexit.register(unlock)

        return wrap_func

    return decorator


def unique_scheduled_v3(func):
    def wrap_func(*args, **kwargs):
        lock_file_name = func.__name__.upper() + ".LOCK"

        with open(lock_file_name, "wb") as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            func(*args, **kwargs)

    return wrap_func


unique_scheduled = unique_scheduled_v2
unique_process = unique_scheduled_v3
