"""
Driver Dynamics Lab
Slug Utility
"""


def slugify(text: str) -> str:
    """Convert text to a filesystem-friendly slug."""
    return (
        text.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )