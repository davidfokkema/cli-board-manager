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
    BINDINGS = [("c", "clear", "Clear")]

    current_item: ClipItem | None = None

    def on_mount(self) -> None:
        self.set_interval(0.2, self.watch_clipboard)

    def watch_clipboard(self) -> None:
        contents = pyperclip.paste()
        if contents != self.current_contents():
            self.append(item := ClipItem(contents=contents))
            self.set_current_item(item)

    def current_contents(self) -> str:
        if self.current_item:
            return self.current_item.contents
        else:
            return ""

    @on(ListView.Selected)
    def copy_contents(self, event: ListView.Selected) -> None:
        self.set_current_item(event.item)
        pyperclip.copy(self.current_item.contents)
        self.notify("Copied contents to clipboard.")

    def set_current_item(self, item):
        if self.current_item:
            self.current_item.remove_class("current")
        item.add_class("current")
        # self.parent.scroll_visible(item)
        self.current_item = item

    def action_clear(self) -> None:
        self.clear()


class CliBoardManagerApp(App[None]):
    CSS_PATH = "app.tcss"

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with VerticalScroll():
            yield ClipBoard(id="clipboard")

    def action_quit(self):
        self.exit()


if __name__ == "__main__":
    CliBoardManagerApp().run()
