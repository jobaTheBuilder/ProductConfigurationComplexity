import argparse
import logging
from pathlib import Path

from COOM2AnalysisKnowledgeGraph import COOM2AnalysisKnowledgeGraph
from KGDescribe import KGDescribe


class COOMDescribe:
    def __init__(self, inputfile: Path):
        self.inputfile = inputfile

    def describe(self) -> None:
        """Convert one COOM model and print the configured complexity measures.

        The generated analysis graph is written next to the input file and then
        loaded again for SPARQL-based evaluation.
        """
        measure_ws = Path(__file__).parent / "resources" / "measures"
        measures = [
            measure_ws / "component_count.sparql",
            measure_ws / "choice_feature_count.sparql",
            measure_ws / "num_feature_count.sparql",
            measure_ws / "text_feature_count.sparql",
            measure_ws / "knowledge_count.sparql",
            measure_ws / "knowledge_feature_average.sparql",
            measure_ws / "inverse_knowledge_feature_average.sparql",
            measure_ws / "avg_terminology_depth.sparql"
            ]

        converted_graph = self.inputfile.parent / f"{self.inputfile.stem}_analysis.ttl"
        logging.info(f"Converting COOM RDF file to {converted_graph}")
        converter = COOM2AnalysisKnowledgeGraph(self.inputfile)
        converter.export(converted_graph)

        logging.info(f"Describe: {converted_graph}")
        describer = KGDescribe()
        describer.load(converted_graph)
        describer.run_measures(measures)
        describer.describe()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a COOM RDF file and describe the resulting knowledge graph.")
    parser.add_argument("-i", "--inputfile", help="Input COOM RDF file.", required=True)
    return parser.parse_args()


def main() -> None:
    """Parse CLI arguments and run the COOM description pipeline."""
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    app = COOMDescribe(Path(args.inputfile))
    app.describe()


if __name__ == "__main__":
    main()
