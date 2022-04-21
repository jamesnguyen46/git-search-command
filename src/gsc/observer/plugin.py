import os
import click


class ExportPlugin:
    EXTENSION_SUPPORTED = (".md", ".markdown")

    def __init__(self) -> None:
        self._export_file = None

    def set_output_path(self, output_path: str):
        if output_path is None:
            self._export_file = None
            return

        if os.path.splitext(output_path)[1] not in self.EXTENSION_SUPPORTED:
            raise NotImplementedError("Only support markdown file.")

        self._export_file = (
            click.open_file(output_path, mode="w") if output_path else None
        )

    def write(self, message):
        if self._export_file:
            self._export_file.write(message + "\n")

    def write_lines(self):
        if self._export_file:
            self._export_file.write("\n")

    def close(self):
        if self._export_file and not self._export_file.closed:
            self._export_file.close()


class PrintPlugin:
    def __init__(self, is_debug: bool) -> None:
        self.is_debug = is_debug

    def print(self, msg, **styles):
        if self.is_debug:
            return

        click.secho(msg, **styles)
