import abc
from timeit import default_timer as timer
from datetime import timedelta
from typing import Any
from rx.core import Observer
from gsc.presentation.observer.plugin import PrintPlugin, MarkdownExportPlugin


class PrintParam(abc.ABC):
    def __init__(self, **kwargs) -> None:
        self.env_name = kwargs.get("env_name")
        self.keyword = kwargs.get("keyword")
        self.output_path = kwargs.get("output_path")
        self.is_debug = kwargs.get("is_debug")


class BaseObserver(Observer, abc.ABC):
    def __init__(self, param: PrintParam = None) -> None:
        super().__init__()
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


class PrintObserver(BaseObserver):
    def __init__(self, param: PrintParam = None) -> None:
        self.print_output = PrintPlugin(param.is_debug)
        self.export_output = None
        if param.output_path:
            self.export_output = MarkdownExportPlugin()
            self.export_output.set_output_path(param.output_path)
        super().__init__(param)

    def print_title(self, text: str):
        self.print_output.print(text, color="bright_blue")

        if self.export_output:
            self.export_output.heading1(text)

    def print_heading1(self, text: str, dim=False):
        self.print_output.print(text, color="bright_magenta", dim=dim)

        if self.export_output:
            self.export_output.heading2(text)

    def print_heading2(self, text: str, dim=False):
        self.print_output.print(text, color="cyan", dim=dim)

        if self.export_output:
            self.export_output.heading3(text)

    def print(
        self, text: str, background: str = None, color: str = None, dim: bool = False
    ):
        self.print_output.print(text, background, color, dim)

        if self.export_output:
            self.export_output.write(text)

    def print_link(
        self, text: str, background: str = None, color: str = None, dim: bool = False
    ):
        self.print_output.print(text, background, color, dim)

        if self.export_output:
            self.export_output.write(text)

    def print_code_block(self, text: str, highlight_keyword: str):
        # Append indented paragraph for message
        temp_text = "   " + text
        final_text = temp_text.replace("\n", "\n   ")
        self.print_output.print_highlight(final_text, highlight_keyword, dim=True)

        if self.export_output:
            self.export_output.write(f"```\n{text})\n```")

    def print_separate_line(self):
        self.print_output.print("------------------------")

    def print_no_result(self, text: str):
        self.print_output.print(text, dim=True)

        if self.export_output:
            self.export_output.write(f"~~{text})~~")

    def dispose(self) -> None:
        self.export_output.close()
        return super().dispose()
