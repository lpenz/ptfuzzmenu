"""Fuzzy-filtering menu widget for prompt-toolkit"""

import importlib.metadata

from .fuzzmenu import FuzzMenu
from .vmenu import VMenu


def version() -> str:
    return importlib.metadata.version("ptfuzzmenu")


__all__ = [
    "version",
    "VMenu",
    "FuzzMenu",
]
