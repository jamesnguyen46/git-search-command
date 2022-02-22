import multiprocessing
from rx.scheduler import ThreadPoolScheduler


class BaseUseCase:
    def __init__(self) -> None:
        optimal_thread_count = multiprocessing.cpu_count()
        self.pool_scheduler = ThreadPoolScheduler(optimal_thread_count)
