import abc
import click


class ExportPlugin(abc.ABC):
    def __init__(self) -> None:
        self._export_file = None

    def set_output_path(self, output_path: str):
        if output_path is None:
            self._export_file = None
            return

        self._export_file = (
            click.open_file(output_path, mode="w") if output_path else None
        )

    def write(self, message: str):
        if self._export_file:
            self._export_file.write(message + "\n")

    def close(self):
        if self._export_file and not self._export_file.closed:
            self._export_file.close()


class MarkdownExportPlugin(ExportPlugin):
    def heading1(self, text: str):
        self.write(f"\n# {text}\n")

    def heading2(self, text: str):
        self.write(f"\n## {text}\n")

    def heading3(self, text: str):
        self.write(f"\n### {text}\n")

    def normal(self, text: str):
        self.write(text)

    def hyperlink(self, text: str, link: str):
        self.write(f"[{text}]({link})")

    def code_block(self, text: str):
        self.write(f"```\n{text})\n```")


class PrintPlugin:
    def __init__(self, is_debug: bool) -> None:
        self.is_debug = is_debug

    def print(
        self, msg: str, background: str = None, color: str = None, dim: bool = False
    ):
        """
        Print the message to console.

        Input param :

        - color: set the foreground color of message.
        - background: set the background color of message.
        - dim: enable or disable dim mode.

        Supported color names :

            * ``black`` (might be a gray)
            * ``red``
            * ``green``
            * ``yellow`` (might be an orange)
            * ``blue``
            * ``magenta``
            * ``cyan``
            * ``white`` (might be light gray)
            * ``bright_black``
            * ``bright_red``
            * ``bright_green``
            * ``bright_yellow``
            * ``bright_blue``
            * ``bright_magenta``
            * ``bright_cyan``
            * ``bright_white``

        """
        if self.is_debug:
            return

        click.secho(msg, bg=background, fg=color, dim=dim)

    def print_highlight(self, msg: str, highlight_text: str, **styles):
        # Set background style for text which need to be highlighted
        formated_text = click.style(highlight_text, bg="bright_white")
        # Split the original text and join highlight text
        split_msg_arr = [
            click.style(msg, dim=True) for msg in msg.split(highlight_text)
        ]
        final_msg = formated_text.join(split_msg_arr)

        self.print(
            final_msg, styles.get("background"), styles.get("color"), styles.get("dim")
        )
