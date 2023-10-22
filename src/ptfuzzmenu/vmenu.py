"""Vertical menu widget for prompt-toolkit"""

from typing import Any, Callable, Optional, Sequence, Sized, cast

from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Container, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType

E = KeyPressEvent


class VMenu:
    def __init__(
        self,
        items: Sequence[tuple[str, Any]],
        handle_current: Optional[Callable[[str, Any], None]] = None,
        handle_enter: Optional[Callable[[str, Any], None]] = None,
    ):
        self.items = items
        self._handle_current = handle_current
        self._handle_enter = handle_enter
        self.current_item = self.items[0]
        self.current_index = 0
        self.control = FormattedTextControl(
            self._get_text_fragments,
            key_bindings=self._get_key_bindings(),
            focusable=True,
        )
        self.window = Window(
            self.control,
            width=self.width,
            style=self.get_style,
        )

    def width(self) -> int:
        return max([len(cast(Sized, i[0])) for i in self.items])

    def get_style(self) -> str:
        if get_app().layout.has_focus(self.window):
            return "class:fuzzmenu.focused"
        else:
            return "class:fuzzmenu.unfocused"

    def _get_text_fragments(self) -> StyleAndTextTuples:
        def mouse_handler(mouse_event: MouseEvent) -> None:
            if mouse_event.event_type == MouseEventType.MOUSE_UP:
                self.current_index = mouse_event.position.y

        result: StyleAndTextTuples = []
        for i, item in enumerate(self.items):
            current = i == self.current_index
            if current:
                result.append(("[SetCursorPosition]", ""))
            if current:
                result.append(("class:fuzzmenu.current", item[0]))
            else:
                result.append(("class:fuzzmenu.item", item[0]))
            result.append(("", "\n"))
        # Add mouse handler to all fragments.
        for i in range(len(result)):
            result[i] = (result[i][0], result[i][1], mouse_handler)
        result.pop()  # Remove last newline.
        return result

    def handle_current(self) -> None:
        if self._handle_current is not None:
            (label, item) = self.items[self.current_index]
            self._handle_current(label, item)

    def handle_enter(self) -> None:
        if self._handle_enter is not None:
            (label, item) = self.items[self.current_index]
            self._handle_enter(label, item)

    def _get_key_bindings(self) -> KeyBindings:
        "Key bindings for the Button."
        kb = KeyBindings()

        @kb.add("c-home")
        def _first(event: E) -> None:
            self.current_index = 0
            self.handle_current()

        @kb.add("c-end")
        def _last(event: E) -> None:
            self.current_index = len(self.items) - 1
            self.handle_current()

        @kb.add("up")
        def _up(event: E) -> None:
            self.current_index = max(0, self.current_index - 1)
            self.handle_current()

        @kb.add("down")
        def _down(event: E) -> None:
            self.current_index = min(len(self.items) - 1, self.current_index + 1)
            self.handle_current()

        @kb.add("pageup")
        def _pageup(event: E) -> None:
            w = event.app.layout.current_window
            if w.render_info:
                self.current_index = max(
                    0, self.current_index - len(w.render_info.displayed_lines)
                )
            self.handle_current()

        @kb.add("pagedown")
        def _pagedown(event: E) -> None:
            w = event.app.layout.current_window
            if w.render_info:
                self.current_index = min(
                    len(self.items) - 1,
                    self.current_index + len(w.render_info.displayed_lines),
                )
            self.handle_current()

        @kb.add(" ")
        @kb.add("enter")
        def _(event: E) -> None:
            self.handle_enter()

        return kb

    def __pt_container__(self) -> Container:
        return self.window
