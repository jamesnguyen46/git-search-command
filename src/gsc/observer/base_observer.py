import abc
from timeit import default_timer as timer
from datetime import timedelta
from typing import Any
from rx.core import Observer
from gsc.observer.plugin import PrintPlugin, ExportPlugin


class PrintParam(abc.ABC):
    def __init__(self, **kwargs) -> None:
        self.env_name = kwargs.get("env_name")
        self.keyword = kwargs.get("keyword")
        self.output_path = kwargs.get("output_path")
        self.is_debug = kwargs.get("is_debug")


class BasePrintObserver(Observer, abc.ABC):
    def __init__(self, param: PrintParam = None) -> None:
        super().__init__()
        self.print_output = PrintPlugin(param.is_debug)
        self.export_output = ExportPlugin()
        self.export_output.set_output_path(param.output_path)
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

    def write(self, message):
        self.export_output.write(message)

    def write_lines(self):
        self.export_output.write_lines()

    def print(self, msg, **styles):
        self.print_output.print(msg, **styles)

    def on_next(self, value: Any) -> None:
        self.on_print_result(value)

    def on_completed(self) -> None:
        elapsed_time = timedelta(seconds=timer() - self.start_time)
        self.on_print_end(elapsed_time)

    def on_error(self, error: Exception) -> None:
        self.on_print_error(error)

    def dispose(self) -> None:
        self.param = None
        self.close()
        return super().dispose()
