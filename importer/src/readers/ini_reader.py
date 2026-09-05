from pathlib import Path
import configparser


class IniReader:
    @staticmethod
    def read(file_path: Path) -> dict:
        # ❗ interpolation deaktivieren
        config = configparser.ConfigParser(interpolation=None)
        config.read(file_path)

        data = {}

        for section in config.sections():
            for key, value in config.items(section):
                data[key] = value

        return data