import pyperclip
from textual.app import App, ComposeResult, on
from textual.containers import Horizontal, Vertical
from textual.events import AppFocus, Event
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.timer import Timer
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


class EditScreen(ModalScreen):
    def __init__(self, contents: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.contents = contents

    def compose(self) -> ComposeResult:
        with Vertical():
            yield TextArea(text=self.contents, show_line_numbers=1)
            with Horizontal(id="buttons"):
                yield Button("Done", id="done", variant="primary")
                yield Button("Cancel", id="cancel", variant="error")

    @on(Button.Pressed, "#done")
    def finish(self) -> None:
        self.dismiss(self.query_one(TextArea).text)

    @on(Button.Pressed, "#cancel")
    def cancel(self) -> None:
        self.dismiss(False)


class ClipBoardItem(ListItem):
    class Deleted(Event):
        def __init__(self, item: "ClipBoardItem") -> None:
            super().__init__()
            self.item = item

    contents = reactive("", recompose=True)

    def __init__(self, contents: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.contents = contents

    def compose(self) -> ComposeResult:
        yield Label(self.contents, id="contents")
        with Horizontal():
            yield Button("Edit", id="edit", variant="primary")
            yield Button("Delete", id="delete", variant="error")

    @on(Button.Pressed, "#delete")
    def remove_item(self) -> None:
        self.post_message(self.Deleted(item=self))

    @on(Button.Pressed, "#edit")
    def edit_item(self) -> None:
        self.app.push_screen(EditScreen(self.contents), callback=self.replace_contents)

    def replace_contents(self, contents: bool | str) -> None:
        if contents is not False:
            self.contents = contents

    def watch_contents(self, old_contents: str, new_contents: str) -> None:
        if self.has_class("current"):
            pyperclip.copy(new_contents)


class ClipBoardHistoryItem(ClipBoardItem):

    class AppendToWorkflow(Event):
        def __init__(self, contents: str) -> None:
            super().__init__()
            self.contents = contents

    def compose(self) -> ComposeResult:
        yield Label(self.contents)
        with Horizontal():
            yield Button("Add to workflow", id="append_workflow")
            yield Button("Edit", id="edit", variant="primary")
            yield Button("Delete", id="delete", variant="error")

    @on(Button.Pressed, "#append_workflow")
    def append_to_workflow(self, event: Button.Pressed) -> None:
        self.post_message(self.AppendToWorkflow(contents=self.contents))


class WorkflowItem(ClipBoardItem): ...


class ClipBoardView(ListView):
    BINDINGS = [("c", "clear", "Clear")]

    current_item: ClipBoardItem | None = None

    def current_contents(self) -> str:
        if self.current_item:
            return self.current_item.contents
        else:
            return ""

    @on(ListView.Selected)
    def copy_selected_contents(self, event: ListView.Selected) -> None:
        self.copy_contents(event.item)

    @on(ClipBoardItem.Deleted)
    def delete_item(self, event: ClipBoardItem.Deleted) -> None:
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

    def copy_contents(self, item: ClipBoardItem) -> None:
        self.set_current_item(item)
        pyperclip.copy(self.current_item.contents)
        self.notify("Copied contents to clipboard.")

    def set_current_item(self, item: ClipBoardItem | None) -> None:
        if self.current_item:
            self.current_item.remove_class("current")
        if item is not None:
            item.add_class("current")
            item.scroll_visible()
        self.current_item = item

    def action_clear(self) -> None:
        self.clear_clipboard()
        self.clear()

    def clear_clipboard(self):
        self.current_item = None
        pyperclip.copy("")


class WorkFlow(ClipBoardView):
    def start_workflow(self) -> None:
        self.post_message(ListView.Selected(list_view=self, item=self.children[0]))

    def next_workflow_step(self) -> None:
        idx = self.children.index(self.current_item)
        try:
            self.copy_contents(self.children[idx + 1])
        except IndexError:
            self.copy_contents(self.children[0])


class ClipBoardHistory(ClipBoardView):

    timer: Timer
    workflow: WorkFlow

    def __init__(self, workflow: WorkFlow, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.workflow = workflow

    def on_mount(self) -> None:
        self.timer = self.set_interval(0.2, self.watch_clipboard)

    def watch_clipboard(self) -> None:
        contents = pyperclip.paste()
        if (
            contents != self.current_contents()
            and contents != self.workflow.current_contents()
        ):
            self.append(item := ClipBoardHistoryItem(contents=contents))
            self.set_current_item(item)
            self.parent.post_message(
                ClipBoardHistory.Selected(list_view=self, item=item)
            )


class CliBoardManagerApp(App[None]):
    CSS_PATH = "app.tcss"

    BINDINGS = [("q", "quit", "Quit")]

    workflow_is_running = False

    def compose(self) -> ComposeResult:
        yield Header(icon="📋")
        yield Footer()
        with TabbedContent(id="tabs"):
            self.workflow = WorkFlow(id="workflow")
            self.history = ClipBoardHistory(
                workflow=self.workflow, id="clipboard_history"
            )
            with TabPane("History", id="tab_history"):
                yield self.history
            with TabPane("Workflow", id="tab_workflow"):
                yield self.workflow
                with Horizontal(id="workflow_buttons"):
                    yield Button(
                        "Start workflow", id="start_workflow", variant="success"
                    )
                    yield Button(
                        "Stop", id="stop_workflow", variant="error", disabled=True
                    )

    @on(ClipBoardHistoryItem.AppendToWorkflow)
    def append_to_workflow(self, event: ClipBoardHistoryItem.AppendToWorkflow) -> None:
        self.workflow.append(WorkflowItem(event.contents))

    @on(ListView.Selected, "#clipboard_history")
    def history_item_selected(self, event):
        self.workflow.set_current_item(None)

    @on(ListView.Selected, "#workflow")
    def workflow_item_selected(self, event):
        self.query_one("#clipboard_history").set_current_item(None)

    @on(Button.Pressed, "#start_workflow")
    def start_workflow(self) -> None:
        self.query_one("#tabs").disable_tab("tab_history")
        self.query_one("#start_workflow").disabled = True
        self.query_one("#stop_workflow").disabled = False
        self.workflow.start_workflow()
        self.history.timer.pause()
        self.workflow_is_running = True

    @on(Button.Pressed, "#stop_workflow")
    def stop_workflow(self) -> None:
        self.query_one("#tabs").enable_tab("tab_history")
        self.query_one("#start_workflow").disabled = False
        self.query_one("#stop_workflow").disabled = True
        self.workflow_is_running = False
        self.history.timer.resume()

    @on(AppFocus)
    def next_workflow_step(self) -> None:
        if self.workflow_is_running:
            self.workflow.next_workflow_step()

    def action_quit(self):
        self.exit()


def main():
    CliBoardManagerApp().run()


if __name__ == "__main__":
    main()
