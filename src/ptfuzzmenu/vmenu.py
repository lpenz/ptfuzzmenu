"""Vertical menu widget for prompt-toolkit"""

from functools import wraps
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
        focusable: bool = True,
    ):
        self.items = items
        self._handle_current = handle_current
        self._handle_enter = handle_enter
        self.current_item: Optional[tuple[str, Any]] = self.items[0]
        self.current_index: Optional[int] = 0
        self.control = FormattedTextControl(
            self._get_text_fragments,
            key_bindings=self._get_key_bindings(),
            focusable=focusable,
        )
        self.window = Window(
            self.control,
            width=max([len(cast(Sized, i[0])) for i in self.items]),
            style=self.get_style,
        )
        self.handle_current()

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
        self.current_index = None
        for i, item in enumerate(self.items):
            current = item == self.current_item
            if current:
                self.current_index = i
                result.append(("[SetCursorPosition]", ""))
                result.append(("class:fuzzmenu.current", item[0]))
            else:
                result.append(("class:fuzzmenu.item", item[0]))
            result.append(("", "\n"))
        # Add mouse handler to all fragments.
        for i in range(len(result)):
            result[i] = (result[i][0], result[i][1], mouse_handler)
        if result:
            result.pop()  # Remove last newline.
        return result

    def handle_current(self) -> None:
        if self._handle_current is not None and self.current_index is not None:
            (label, item) = self.items[self.current_index]
            self._handle_current(label, item)

    def handle_enter(self) -> None:
        if self._handle_enter is not None and self.current_index is not None:
            (label, item) = self.items[self.current_index]
            self._handle_enter(label, item)

    def fix(self) -> None:
        if not self.items:
            self.current_item = None
            self.current_index = None
            return
        if self.current_item is None:
            self.current_item = self.items[0]
            self.current_index = 0
            return
        if self.current_index is None:
            for i, item in enumerate(self.items):
                if item == self.current_item:
                    self.current_index = i
                    return
            self.current_index = 0
        self.current_index = max(0, self.current_index)
        self.current_index = min(len(self.items) - 1, self.current_index)
        self.current_item = self.items[self.current_index]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        def wrapper(func: Callable[[E], None]) -> Callable[[E], None]:
            @wraps(func)
            def inner(event: E) -> None:
                if not self.items:
                    return
                self.fix()
                func(event)
                if self.current_index is None or self.current_index < 0:
                    self.current_index = 0
                self.current_index = min(len(self.items) - 1, self.current_index)
                self.current_item = self.items[self.current_index]
                self.handle_current()

            return inner

        @kb.add("c-home")
        @wrapper
        def _first(event: E) -> None:
            self.current_index = 0

        @kb.add("c-end")
        @wrapper
        def _last(event: E) -> None:
            self.current_index = len(self.items) - 1

        @kb.add("up")
        @wrapper
        def _up(event: E) -> None:
            assert self.current_index is not None
            self.current_index = self.current_index - 1

        @kb.add("down")
        @wrapper
        def _down(event: E) -> None:
            assert self.current_index is not None
            self.current_index = self.current_index + 1

        @kb.add("pageup")
        @wrapper
        def _pageup(event: E) -> None:
            w = self.window
            if w.render_info:
                assert self.current_index is not None
                self.current_index -= len(w.render_info.displayed_lines)

        @kb.add("pagedown")
        @wrapper
        def _pagedown(event: E) -> None:
            w = self.window
            if w.render_info:
                assert self.current_index is not None
                self.current_index += len(w.render_info.displayed_lines)

        @kb.add(" ")
        @kb.add("enter")
        def _(event: E) -> None:
            self.handle_enter()

        return kb

    def __pt_container__(self) -> Container:
        return self.window
