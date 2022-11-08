import multiprocessing

event = multiprocessing.Event()


def keep_main_thread_running(function):
    def inner(*args, **kwargs):
        if event.is_set():
            event.clear()

        function(*args, **kwargs)

        event.wait()

    return inner


def finish_main_thread(function):
    def inner(*args, **kwargs):

        function(*args, **kwargs)

        if not event.is_set():
            event.set()

    return inner
