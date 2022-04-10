import abc
import os.path
from typing import Any, Optional
import click
from rx.core import typing, Observer


class PrintParam(abc.ABC):
    def __init__(self, **kwargs) -> None:
        self.env_name = kwargs.get("env_name")
        self.keyword = kwargs.get("keyword")
        self.output_path = kwargs.get("output_path")


class BasePrintObserver(Observer, abc.ABC):
    MARKDOWN_EXTENSION = (".md", ".markdown")

    def __init__(
        self,
        on_next: Optional[typing.OnNext] = None,
        on_error: Optional[typing.OnError] = None,
        on_completed: Optional[typing.OnCompleted] = None,
        param: PrintParam = None,
    ) -> None:
        super().__init__(on_next, on_error, on_completed)
        self.param = param
        self._is_markdown = False
        self._export_file = None
        if self.param.output_path:
            path = self.param.output_path
            self._is_markdown = os.path.splitext(path)[1] in self.MARKDOWN_EXTENSION
            self._export_file = click.open_file(path, mode="w") if path else None
        self.on_print_start()

    @abc.abstractmethod
    def on_print_start(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def on_print_result(self, value: Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def on_print_end(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def on_print_error(self, error: Exception) -> None:
        raise NotImplementedError

    def echo(self, msg, url=None, **styles):
        click.secho(msg, **styles)

        if self._export_file:
            message = f"[{msg}]({url})" if url and self._is_markdown else msg
            self._export_file.write(message + "\n")

    def on_next(self, value: Any) -> None:
        self.on_print_result(value)

    def on_completed(self) -> None:
        self.on_print_end()
        if self._export_file:
            self._export_file.close()
            self._export_file = None

    def on_error(self, error: Exception) -> None:
        self.on_print_error(error)
        if self._export_file:
            self._export_file.close()
            self._export_file = None

    def dispose(self) -> None:
        self.param = None
        return super().dispose()
