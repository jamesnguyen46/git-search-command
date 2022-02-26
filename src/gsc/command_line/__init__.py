import multiprocessing

event = multiprocessing.Event()


def block_main_thread(function):
    def inner(*args, **kwargs):
        if event.is_set():
            event.clear()

        function(*args, **kwargs)

        event.wait()

    return inner


def release_main_thread(function):
    def inner(*args, **kwargs):

        function(*args, **kwargs)

        if not event.is_set():
            event.set()

    return inner
