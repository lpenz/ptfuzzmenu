"""Vertical menu widget for prompt-toolkit"""

from functools import wraps
from typing import Any, Callable, Optional, Sequence, Sized, cast

from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text.base import OneStyleAndTextTuple, StyleAndTextTuples
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Container, Window
from prompt_toolkit.layout.controls import FormattedTextControl

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
            self._gen_text_fragments,
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

    def _gen_text_fragment_tuple(
        self, item: Any, current: bool, last: bool
    ) -> OneStyleAndTextTuple:
        if current:
            style = "[SetCursorPosition] class:fuzzmenu.current"
        else:
            style = "class:fuzzmenu.item"
        suffix = "\n" if not last else ""
        return (style, item[0] + suffix)

    def _gen_text_fragments(self) -> StyleAndTextTuples:
        result: StyleAndTextTuples = []
        self.current_index = None
        for i, item in enumerate(self.items):
            current = item == self.current_item
            last = i == len(self.items) - 1
            result.append(self._gen_text_fragment_tuple(item, current, last))
            if current:
                self.current_index = i
        return result

    def handle_current(self) -> None:
        if self._handle_current is not None and self.current_index is not None:
            (label, item) = self.items[self.current_index]
            self._handle_current(label, item)

    def handle_enter(self) -> None:
        if self._handle_enter is not None and self.current_index is not None:
            (label, item) = self.items[self.current_index]
            self._handle_enter(label, item)

    def sanitize(self) -> None:
        if not self.items:
            # Only situation where the self.current_item/index members
            # are None
            self.current_item = None
            self.current_index = None
            return
        # Fix a self.current_item by setting it to the first item:
        if self.current_item is None or self.current_item not in self.items:
            self.current_item = self.items[0]
            self.current_index = 0
            return
        # Fix self.current_index == None by using self.current_item, which
        # is valid here:
        if self.current_index is None:
            for i, item in enumerate(self.items):
                if item == self.current_item:
                    self.current_index = i
                    return
            self.current_index = 0
        # self.current_index is not None; fix values out-of-bounds:
        self.current_index = max(0, self.current_index)
        self.current_index = min(len(self.items) - 1, self.current_index)
        self.current_item = self.items[self.current_index]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        def wrapper(func: Callable[[E], None]) -> Callable[[E], None]:
            @wraps(func)
            def inner(event: E) -> None:
                self.sanitize()
                if not self.items:
                    return
                # self.current_item/index are only None if items is empty;
                # so they are not None here:
                assert self.current_item is not None
                assert self.current_index is not None
                previous = self.current_item
                func(event)
                if self.current_index < 0:
                    self.current_index = 0
                self.current_index = min(len(self.items) - 1, self.current_index)
                self.current_item = self.items[self.current_index]
                if self.current_item != previous:
                    self.handle_current()

            return inner

        @kb.add("c-home")
        @kb.add("escape", "home")
        @wrapper
        def _first(event: E) -> None:
            self.current_index = 0

        @kb.add("c-end")
        @kb.add("escape", "end")
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
        def _enter(event: E) -> None:
            self.handle_enter()

        return kb

    def __pt_container__(self) -> Container:
        return self.window
