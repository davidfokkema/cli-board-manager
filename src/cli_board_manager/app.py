import pyperclip
from textual.app import App, ComposeResult, on
from textual.containers import Horizontal
from textual.events import Event
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


class WorkflowItem(ListItem):

    class Deleted(Event):
        def __init__(self, item: "WorkflowItem", *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.item = item

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
        self.post_message(self.Deleted(item=self))


class WorkFlow(ListView):
    BINDINGS = [("c", "clear", "Clear")]

    current_item: WorkflowItem | None = None

    @on(ListView.Selected)
    def copy_selected_contents(self, event: ListView.Selected) -> None:
        self.copy_contents(event.item)

    def copy_contents(self, item: WorkflowItem) -> None:
        self.set_current_item(item)
        pyperclip.copy(self.current_item.contents)
        self.notify("Copied contents to clipboard.")

    def set_current_item(self, item: WorkflowItem) -> None:
        if self.current_item:
            self.current_item.remove_class("current")
        item.add_class("current")
        item.scroll_visible()
        self.current_item = item

    def action_clear(self) -> None:
        self.clear_clipboard()
        self.clear()

    @on(WorkflowItem.Deleted)
    def delete_item(self, event: WorkflowItem.Deleted) -> None:
        event.item.remove()

    def clear_clipboard(self):
        self.current_item = None
        pyperclip.copy("")


class ClipItem(ListItem):

    class Deleted(Event):
        def __init__(self, item: "ClipItem") -> None:
            super().__init__()
            self.item = item

    class AppendToWorkflow(Event):
        def __init__(self, contents: str) -> None:
            super().__init__()
            self.contents = contents

    def __init__(self, contents: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.contents = contents

    def compose(self) -> ComposeResult:
        yield Label(self.contents)
        with Horizontal():
            yield Button("Add to workflow", id="append_workflow")
            yield Button("Delete", id="delete", variant="error")

    @on(Button.Pressed, "#delete")
    def remove_item(self, event: Button.Pressed) -> None:
        self.post_message(self.Deleted(item=self))

    @on(Button.Pressed, "#append_workflow")
    def append_to_workflow(self, event: Button.Pressed) -> None:
        self.post_message(self.AppendToWorkflow(contents=self.contents))


class ClipBoard(ListView):
    BINDINGS = [("c", "clear", "Clear")]

    current_item: ClipItem | None = None

    def on_mount(self) -> None:
        self.set_interval(0.2, self.watch_clipboard)

    def watch_clipboard(self) -> None:
        contents = pyperclip.paste()
        if contents != self.current_contents():
            print(f"Added value from clipboard, {self=}")
            self.append(item := ClipItem(contents=contents))
            self.set_current_item(item)

    def current_contents(self) -> str:
        if self.current_item:
            return self.current_item.contents
        else:
            return ""

    @on(ListView.Selected)
    def copy_selected_contents(self, event: ListView.Selected) -> None:
        self.copy_contents(event.item)

    def copy_contents(self, item: ClipItem) -> None:
        self.set_current_item(item)
        pyperclip.copy(self.current_item.contents)
        self.notify("Copied contents to clipboard.")

    def set_current_item(self, item: ClipItem) -> None:
        if self.current_item:
            self.current_item.remove_class("current")
        item.add_class("current")
        item.scroll_visible()
        self.current_item = item

    def action_clear(self) -> None:
        self.clear_clipboard()
        self.clear()

    @on(ClipItem.Deleted)
    def delete_item(self, event: ClipItem.Deleted) -> None:
        if event.item == self.current_item:
            idx = self.children.index(event.item)
            try:
                new_current_item = self.children[idx + 1]
            except IndexError:
                if idx > 0:
                    new_current_item = self.children[idx - 1]
                else:
                    new_current_item = None
            if new_current_item is not None:
                self.copy_contents(new_current_item)
            else:
                self.clear_clipboard()
        event.item.remove()

    def clear_clipboard(self):
        self.current_item = None
        pyperclip.copy("")


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

    @on(ClipItem.AppendToWorkflow)
    def append_to_workflow(self, event: ClipItem.AppendToWorkflow) -> None:
        self.query_one("#workflow").append(
            WorkflowItem(event.contents, is_workflow=True)
        )

    def action_quit(self):
        self.exit()


if __name__ == "__main__":
    CliBoardManagerApp().run()
