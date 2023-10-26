"""Fuzzy-filtering menu widget for prompt-toolkit"""

import re
from typing import Callable, Optional, Sequence

from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import Container, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl

from .vmenu import Item, VMenu

E = KeyPressEvent


class FuzzMenu:
    def __init__(
        self,
        items: Sequence[Item],
        current_handler: Optional[Callable[[Item], None]] = None,
        accept_handler: Optional[Callable[[Item], None]] = None,
    ):
        self.items = items
        self.filtered_items = items
        self.vmenu = _FuzzVMenu(
            self, current_handler=current_handler, accept_handler=accept_handler
        )
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
        self.vmenu.handle_current()

    def __pt_container__(self) -> Container:
        return self.window


class _FuzzVMenu(VMenu):
    def __init__(
        self,
        fuzzmenu: FuzzMenu,
        current_handler: Optional[Callable[[Item], None]] = None,
        accept_handler: Optional[Callable[[Item], None]] = None,
    ):
        self.fuzzmenu = fuzzmenu
        VMenu.__init__(
            self,
            fuzzmenu.filtered_items,
            current_handler=current_handler,
            accept_handler=accept_handler,
            focusable=False,
        )

    def get_style(self) -> str:
        if get_app().layout.has_focus(self.fuzzmenu.window):
            return "class:fuzzmenu.focused"
        else:
            return "class:fuzzmenu.unfocused"
