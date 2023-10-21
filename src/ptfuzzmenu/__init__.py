"""Fuzzy-filtering menu widget for prompt-toolkit"""

import importlib.metadata


def version() -> str:
    return importlib.metadata.version("ptfuzzmenu")
