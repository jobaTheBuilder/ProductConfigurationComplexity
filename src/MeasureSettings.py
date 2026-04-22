from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class MeasureDefinition:
    name: str
    path: Path


class MeasureSettings:
    """Load and validate the SPARQL measure list from a YAML settings file."""

    def __init__(self, settings_file: str):
        self.settings_path = Path(settings_file)

    def load_measure_definitions(self) -> List[MeasureDefinition]:
        if not self.settings_path.is_file():
            raise ValueError(f"Settings file does not exist: {self.settings_path}")

        measure_definitions = self._parse_measure_settings()
        missing_measure_files = [measure.path for measure in measure_definitions if not measure.path.is_file()]
        if missing_measure_files:
            missing_files = ", ".join(str(measure_file.name) for measure_file in missing_measure_files)
            raise ValueError(
                f"Measure files defined in {self.settings_path.name} do not exist: {missing_files}"
            )

        return measure_definitions

    def _parse_measure_settings(self) -> List[MeasureDefinition]:
        measure_definitions: List[MeasureDefinition] = []
        inside_measures = False
        current_item: dict[str, str] | None = None

        for raw_line in self.settings_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            if not line:
                continue

            stripped_line = line.strip()
            if not inside_measures:
                if stripped_line == "measures:":
                    inside_measures = True
                    continue
                raise ValueError(
                    f"Unsupported settings format in {self.settings_path.name}: expected a top-level 'measures:' list"
                )

            if stripped_line.startswith("- "):
                if current_item is not None:
                    measure_definitions.append(self._measure_definition_from_item(current_item))

                item_content = stripped_line[2:].strip()
                if not item_content:
                    raise ValueError(f"Unsupported settings format in {self.settings_path.name}: empty measure entry")

                if ":" not in item_content:
                    measure_file = item_content
                    current_item = {
                        "name": Path(measure_file).stem,
                        "file": measure_file,
                    }
                    continue

                key, value = self._split_key_value(item_content)
                current_item = {key: value}
                continue

            if current_item is None:
                raise ValueError(
                    f"Unsupported settings format in {self.settings_path.name}: expected list items below 'measures:'"
                )

            key, value = self._split_key_value(stripped_line)
            current_item[key] = value

        if current_item is not None:
            measure_definitions.append(self._measure_definition_from_item(current_item))

        if not inside_measures:
            raise ValueError(
                f"Unsupported settings format in {self.settings_path.name}: missing top-level 'measures:'"
            )
        if not measure_definitions:
            raise ValueError(f"Unsupported settings format in {self.settings_path.name}: no measures defined")

        return measure_definitions

    def _measure_definition_from_item(self, item: dict[str, str]) -> MeasureDefinition:
        name = item.get("name")
        measure_file = item.get("file")
        if not name or not measure_file:
            raise ValueError(
                f"Unsupported settings format in {self.settings_path.name}: each measure needs 'name' and 'file'"
            )
        return MeasureDefinition(name=name, path=self.settings_path.parent / measure_file)

    def _split_key_value(self, line: str) -> tuple[str, str]:
        if ":" not in line:
            raise ValueError(
                f"Unsupported settings format in {self.settings_path.name}: expected 'name:' or 'file:' entries"
            )
        key, value = line.split(":", 1)
        stripped_key = key.strip()
        stripped_value = value.strip()
        if not stripped_key or not stripped_value:
            raise ValueError(
                f"Unsupported settings format in {self.settings_path.name}: invalid key/value entry '{line}'"
            )
        return stripped_key, stripped_value
