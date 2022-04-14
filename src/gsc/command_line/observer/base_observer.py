import abc
from timeit import default_timer as timer
from datetime import timedelta
from typing import Any, Optional
from rx.core import typing, Observer


class PrintParam(abc.ABC):
    def __init__(self, **kwargs) -> None:
        self.env_name = kwargs.get("env_name")
        self.keyword = kwargs.get("keyword")
        self.output_path = kwargs.get("output_path")
        self.is_debug = kwargs.get("is_debug")


class BasePrintObserver(Observer, abc.ABC):
    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: PrintParam = None,
    ) -> None:
        super().__init__(on_next, on_error, on_completed)
        self.param = param
        self.start_time = timer()
        self.on_print_start()

    @abc.abstractmethod
    def on_print_start(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def on_print_result(self, value: Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def on_print_end(self, elapsed_time) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def on_print_error(self, error: Exception) -> None:
        raise NotImplementedError

    def on_next(self, value: Any) -> None:
        self.on_print_result(value)

    def on_completed(self) -> None:
        elapsed_time = timedelta(seconds=timer() - self.start_time)
        self.on_print_end(elapsed_time)

    def on_error(self, error: Exception) -> None:
        self.on_print_error(error)

    def dispose(self) -> None:
        self.param = None
        return super().dispose()
