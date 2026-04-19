
import argparse
import logging
import time
from pathlib import Path

from rdflib import Graph
from typing import List
from ResultPrinter import ResultPrinter


class KGDescribe:
    def __init__(self):
        """Prepare an empty RDF graph and an output formatter for measure results."""
        self.graph = Graph()
        self.filename = None
        self.result_printer = ResultPrinter()

    def load(self, filename: Path) -> None:
        """Load the generated analysis knowledge graph from a Turtle file."""
        self.filename = filename
        self.graph = Graph()
        self.graph.parse(self.filename, format="turtle")

    def run_measures(self, measure_definitions: List[Path]) -> None:
        """Execute all configured SPARQL measures and collect their result rows."""
        start_time = time.perf_counter()
        logging.info("Running measures for input file: %s", self.filename)
        for measure_def in measure_definitions:
            logging.info("Running measure: %s", measure_def)
            query = measure_def.read_text(encoding="utf-8")
            try:
                results = self.graph.query(query)
            except Exception:
                logging.exception("Failed to execute measure %s", measure_def)
                raise
            for row in results:
                self.result_printer.add_row(measure_def.name, str(row["count"].toPython()))
        elapsed = time.perf_counter() - start_time
        logging.info("run_measures completed in %.3f seconds", elapsed)

    def describe(self):
        """Print the collected measure results as a small table."""
        self.result_printer.print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Describe a knowledge graph file.")
    parser.add_argument("-i", "--inputfile", help="Path to the input file on disk.", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    measure_ws = Path(__file__).parent / "resources" / "measures"
    measures = [
        measure_ws / "choice_feature_count.sparql",
        measure_ws / "num_feature_count.sparql",
        measure_ws / "text_feature_count.sparql",
        measure_ws / "feature_choice_count.sparql",
        measure_ws / "component_count.sparql",
        measure_ws / "avg_terminology_depth.sparql",
        measure_ws / "knowledge_count.sparql",
        measure_ws / "knowledge_feature_average.sparql",
        measure_ws / "inverse_knowledge_feature_average.sparql",
    ]
    app = KGDescribe()
    app.load(Path(args.inputfile))
    app.run_measures(measures)
    app.describe()
