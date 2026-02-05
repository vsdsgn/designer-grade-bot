import os


def data_path(*parts: str) -> str:
    base = os.getenv("DATA_DIR", "data")
    return os.path.join(base, *parts)
