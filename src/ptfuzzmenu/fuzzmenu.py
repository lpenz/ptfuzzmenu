"""Fuzzy-filtering menu widget for prompt-toolkit"""

import re
from typing import Any, Callable, Optional, Sequence

from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Container, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl

from .vmenu import VMenu

E = KeyPressEvent


class FuzzMenu:
    def __init__(
        self,
        items: Sequence[tuple[str, Any]],
        handle_current: Optional[Callable[[str, Any], None]] = None,
        handle_enter: Optional[Callable[[str, Any], None]] = None,
    ):
        self.items = items
        self.filtered_items = items
        self._handle_current = handle_current
        self._handle_enter = handle_enter
        self.vmenu = _FuzzVMenu(self)
        self.buffer = Buffer(multiline=False, on_text_changed=self._do_filter)
        self.control = BufferControl(
            buffer=self.buffer, key_bindings=self.vmenu._get_key_bindings()
        )
        self.window = HSplit(
            [
                VSplit([Window(width=1, char="/", height=1), Window(self.control)]),
                self.vmenu,
            ]
        )

    def _do_filter(self, buf: Buffer) -> None:
        text = buf.document.text
        try:
            regex = re.compile(text)
        except re.error:
            return
        self.filtered_items = [item for item in self.items if regex.search(item[0])]
        self.vmenu.items = self.filtered_items
        self.vmenu.current_index = None
        self.vmenu.sanitize()
        self.vmenu.handle_current()

    def handle_current(self, label: str, item: Any) -> None:
        if self._handle_current is not None:
            self._handle_current(label, item)

    def handle_enter(self, label: str, item: Any) -> None:
        if self._handle_enter is not None:
            self._handle_enter(label, item)

    def __pt_container__(self) -> Container:
        return self.window


class _FuzzVMenu(VMenu):
    def __init__(self, fuzzmenu: FuzzMenu):
        self.fuzzmenu = fuzzmenu
        VMenu.__init__(
            self,
            fuzzmenu.filtered_items,
            fuzzmenu.handle_current,
            fuzzmenu.handle_enter,
            focusable=False,
        )

    def get_style(self) -> str:
        if get_app().layout.has_focus(self.fuzzmenu.window):
            return "class:fuzzmenu.focused"
        else:
            return "class:fuzzmenu.unfocused"
