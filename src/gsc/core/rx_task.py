import types
import multiprocessing
from functools import wraps
from rx import create, core, operators as ops
from rx.scheduler import ThreadPoolScheduler

# calculate number of CPUs, then create a ThreadPoolScheduler with that number of threads
optimal_thread_count = multiprocessing.cpu_count()
rx_pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


def rx_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> core.Observable:
        def subscribe(observer, _=None):
            try:
                res = func(*args, **kwargs)
                observer.on_next(res)
                observer.on_completed()
            except Exception as err:
                observer.on_error(err)

        return create(subscribe).pipe(ops.subscribe_on(rx_pool_scheduler), __flat_map())

    return wrapper


def __flat_map():
    def _flat_map(source):
        def subscribe(observer, scheduler=None):
            def emit(value):
                if isinstance(value, list):
                    for item in value:
                        observer.on_next(item)
                else:
                    observer.on_next(value)

            def on_next(value):
                if isinstance(value, types.GeneratorType):
                    for data in value:
                        emit(data)
                else:
                    emit(value)

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler
            )

        return create(subscribe)

    return _flat_map
