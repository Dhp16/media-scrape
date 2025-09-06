import re


def sanitize_filename(name: str) -> str:
    """Removes characters invalid for filenames and replaces spaces."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name.replace(" ", "_").replace(":", "_")  # Also replace colons
    return name[:150]
