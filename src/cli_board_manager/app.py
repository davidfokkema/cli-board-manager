import pyperclip
from textual.app import App, ComposeResult, on
from textual.containers import Horizontal
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    TabbedContent,
    TabPane,
    TextArea,
)


class ClipItem(ListItem):
    def __init__(
        self, contents: str, is_workflow: bool = False, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.contents = contents
        self.is_workflow = is_workflow

    def compose(self) -> ComposeResult:
        yield Label(self.contents)
        with Horizontal():
            if not self.is_workflow:
                yield Button("Add to workflow", id="add_workflow")
            yield Button("Delete", id="delete", variant="error")

    @on(Button.Pressed, "#delete")
    def remove_item(self, event: Button.Pressed) -> None:
        self.remove()


class ClipBoardView(ListView):
    BINDINGS = [("c", "clear", "Clear")]

    current_item: ClipItem | None = None

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
        item.scroll_visible()
        self.current_item = item

    def action_clear(self) -> None:
        self.clear()


class ClipBoard(ClipBoardView):
    def on_mount(self) -> None:
        print(f"Yo, I'm {self=}")
        self.set_interval(0.2, self.watch_clipboard)

    def watch_clipboard(self) -> None:
        contents = pyperclip.paste()
        if contents != self.current_contents():
            print(f"Added value from clipboard, {self=}")
            self.append(item := ClipItem(contents=contents))
            self.set_current_item(item)


class WorkFlow(ClipBoardView): ...


class CliBoardManagerApp(App[None]):
    CSS_PATH = "app.tcss"

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent():
            with TabPane("History", id="tab_history"):
                yield ClipBoard(id="clipboard_history")
            with TabPane("Workflow", id="tab_workflow"):
                yield WorkFlow(id="workflow")

    @on(Button.Pressed, "#add_workflow")
    def add_to_workflow(self, event: Button.Pressed) -> None:
        print(f"{event.button.parent.parent=}")
        self.query_one("#workflow").append(ClipItem("Star", is_workflow=True))

    def action_quit(self):
        self.exit()


if __name__ == "__main__":
    CliBoardManagerApp().run()
