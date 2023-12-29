import importlib.metadata


def version() -> str:
    return importlib.metadata.version("ptfuzzmenu")


__all__ = [
    "version",
]
