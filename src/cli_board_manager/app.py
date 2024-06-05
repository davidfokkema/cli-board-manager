import pyperclip
from textual.app import App, ComposeResult, on
from textual.containers import VerticalScroll
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, TextArea


class ClipItem(ListItem):
    def __init__(self, contents: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.contents = contents

    def compose(self) -> ComposeResult:
        yield Label(self.contents)


class ClipBoard(ListView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        self.set_interval(0.2, self.watch_clipboard)

    def watch_clipboard(self) -> None:
        contents = pyperclip.paste()
        if contents is not None:
            if not self.children or contents != self.children[-1].contents:
                self.append(ClipItem(contents=contents))


class CliBoardManagerApp(App[None]):
    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with VerticalScroll():
            yield ClipBoard(id="clipboard")


if __name__ == "__main__":
    CliBoardManagerApp().run()
