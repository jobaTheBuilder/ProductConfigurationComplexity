from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path
from typing import List

try:
    from rdflib import Graph
except ImportError:  # pragma: no cover - depends on local environment
    Graph = None

from ResultPrinter import ResultPrinter


class KGDescribe:
    def __init__(self):
        """Prepare an empty RDF graph and an output formatter for measure results."""
        if Graph is None:
            raise ImportError("rdflib is required to describe knowledge graphs")
        self.graph = Graph()
        self.filename = None
        self.result_printer = ResultPrinter()

    def load(self, filename: Path) -> None:
        """Load the generated analysis knowledge graph from a Turtle file."""
        self.filename = filename
        self.graph = Graph()
        self.graph.parse(self.filename, format="turtle")

    def run_measures(self, measure_definitions: List[Path]) -> dict:
        """Execute all configured SPARQL measures and return the collected values."""
        logging.info("Running measures for input file: %s", self.filename)
        results_by_measure = {}
        for measure_def in measure_definitions:
            # logging.info("Running measure: %s", measure_def)
            query = measure_def.read_text(encoding="utf-8")
            try:
                results = self.graph.query(query)
            except Exception:
                logging.exception("Failed to execute measure %s", measure_def)
                raise
            for row in results:
                value = str(row["count"].toPython())
                results_by_measure[measure_def.stem] = value
        return results_by_measure

    def describe(self, input_files: List[Path], measure_definitions: List[Path]) -> None:
        """Print the collected measure results as a table with one column per input file."""
        start_time = time.perf_counter()
        self.result_printer = ResultPrinter()
        for input_file in input_files:
            self.load(input_file)
            results_by_measure = self.run_measures(measure_definitions)
            for measure_name, value in results_by_measure.items():
                self.result_printer.add_row(measure_name, value, input_file.stem)
        elapsed = time.perf_counter() - start_time
        logging.info("describe completed in %.3f seconds", elapsed)
        print(self.result_printer.print_as_markdown())

    def load_measure_definitions(self, settings_file: str) -> List[Path]:
        settings_path = Path(settings_file)
        if not settings_path.is_file():
            raise ValueError(f"Settings file does not exist: {settings_path}")

        measure_names = self._parse_measure_settings(settings_path)
        measure_definitions = [settings_path.parent / measure_name for measure_name in measure_names]
        missing_measure_files = [measure_file for measure_file in measure_definitions if not measure_file.is_file()]
        if missing_measure_files:
            missing_files = ", ".join(str(measure_file.name) for measure_file in missing_measure_files)
            raise ValueError(f"Measure files defined in {settings_path.name} do not exist: {missing_files}")

        return measure_definitions

    @staticmethod
    def _parse_measure_settings(settings_path: Path) -> List[str]:
        measure_names: List[str] = []
        inside_measures = False

        for raw_line in settings_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].rstrip()
            if not line:
                continue

            stripped_line = line.strip()
            if not inside_measures:
                if stripped_line == "measures:":
                    inside_measures = True
                    continue
                raise ValueError(
                    f"Unsupported settings format in {settings_path.name}: expected a top-level 'measures:' list"
                )

            if not stripped_line.startswith("- "):
                raise ValueError(
                    f"Unsupported settings format in {settings_path.name}: expected list items below 'measures:'"
                )

            measure_name = stripped_line[2:].strip()
            if not measure_name:
                raise ValueError(f"Unsupported settings format in {settings_path.name}: empty measure entry")
            measure_names.append(measure_name)

        if not inside_measures:
            raise ValueError(f"Unsupported settings format in {settings_path.name}: missing top-level 'measures:'")
        if not measure_names:
            raise ValueError(f"Unsupported settings format in {settings_path.name}: no measures defined")

        return measure_names


def resolve_input_files(inputdir: str) -> List[Path]:
    input_files: List[Path] = []
    if inputdir:
        input_directory = Path(inputdir)
        if not input_directory.is_dir():
            raise ValueError(f"Input directory does not exist or is not a directory: {input_directory}")

        input_files.extend(sorted(input_directory.glob("*.ttl")))

    if not input_files:
        raise ValueError("Provide either -i/--inputfile or -d/--inputdir with Turtle files.")

    return input_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Describe a knowledge graph file by a collection of measures. Measures"
                                                 " are defined in a YAML settings file.")
    parser.add_argument("-d", "--inputdir", help="Directory containing input Turtle files (*.ttl).")
    parser.add_argument(
        "-s",
        "--settings",
        default="all_measures.yaml",
        help="YAML settings file from resources/measures defining the SPARQL measures to run.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    rdf_files = resolve_input_files(args.inputdir)
    app = KGDescribe()
    measures = app.load_measure_definitions(args.settings)
    app.describe(rdf_files, measures)
