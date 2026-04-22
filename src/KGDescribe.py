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

from MeasureSettings import MeasureSettings
from MeasureSettings import MeasureDefinition
from ResultPrinter import ResultPrinter


class KGDescribe:
    def __init__(self, setting_file: str):
        """Prepare an empty RDF graph and an output formatter for measure results."""
        if Graph is None:
            raise ImportError("rdflib is required to describe knowledge graphs")
        self.graph = Graph()
        self.filename = None
        self.result_printer = ResultPrinter()
        self.settings = MeasureSettings(setting_file)
        self.measure_definitions = self.settings.load_measure_definitions()


    def load(self, filename: Path, syntax="turtle") -> None:
            """Load the generated analysis knowledge graph from a RDF file (default is turtle syntax)."""
            self.filename = filename
            self.graph = Graph()
            self.graph.parse(self.filename, format=syntax)

    def run_measures(self, measure_definitions: List[MeasureDefinition]) -> dict:
        """Execute all configured SPARQL measures and return the collected values."""
        logging.info("Running measures for input file: %s", self.filename)
        results_by_measure = {}
        for measure_def in measure_definitions:
            logging.info("Running measure: %s", measure_def)
            query = measure_def.path.read_text(encoding="utf-8")
            try:
                results = self.graph.query(query)
            except Exception:
                logging.exception("Failed to execute measure %s", measure_def.path)
                raise
            for row in results:
                value = str(row["count"].toPython())
                results_by_measure[measure_def.name] = value
        return results_by_measure

    def describe(self, input_files: List[Path]) -> None:
        """Print the collected measure results as a table with one column per input file."""
        start_time = time.perf_counter()
        self.result_printer = ResultPrinter()
        for input_file in input_files:
            self.load(input_file)
            results_by_measure = self.run_measures(self.measure_definitions)
            for measure_name, value in results_by_measure.items():
                self.result_printer.add_row(measure_name, value, input_file.stem)
        elapsed = time.perf_counter() - start_time
        logging.info("describe completed in %.3f seconds", elapsed)
        print(self.result_printer.print_as_markdown())
        output_directory = input_files[0].parent
        output_path = output_directory / "casestudy.tex"
        output_path.write_text(self.result_printer.print_as_latex(), encoding="utf-8")
        logging.info("Wrote LaTeX output to %s", output_path)

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
    app = KGDescribe(args.settings)
    app.describe(rdf_files)
