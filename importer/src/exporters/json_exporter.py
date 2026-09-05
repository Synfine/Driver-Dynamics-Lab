import json
from dataclasses import asdict
from pathlib import Path

from ..models.car import Car


class JsonExporter:
    """Exports domain objects to JSON."""

    @staticmethod
    def export(car: Car, output_file: Path) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(
                asdict(car),
                f,
                indent=4,
                ensure_ascii=False,
            )