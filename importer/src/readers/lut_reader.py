from pathlib import Path


class LutReader:

    @staticmethod
    def read(file_path: Path) -> list[tuple[int, float]]:
        data = []

        if not file_path.exists():
            print(f"⚠️ LUT file not found: {file_path}")
            return data

        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()

                # skip comments / empty
                if not line or line.startswith(";"):
                    continue

                parts = line.split("|")

                if len(parts) != 2:
                    continue

                try:
                    rpm = int(parts[0].strip())
                    power = float(parts[1].strip())
                    data.append((rpm, power))
                except ValueError:
                    continue

        return data