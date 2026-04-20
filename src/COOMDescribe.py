from __future__ import annotations

import argparse
import logging
from pathlib import Path

from RadarVisualizer import RadarVisualizer

RDF_FILE_SUFFIXES = {".rdf", ".ttl", ".owl", ".nt", ".n3", ".xml"}


class COOMDescribe:
    def __init__(self, inputfiles):
        self.inputfiles = inputfiles

    def describe(self):
        """Convert all input models and collect their measure values for radar use."""
        measure_ws = Path(__file__).parent / "resources" / "measures"
        measures = [
            measure_ws / "component_count.sparql",
            measure_ws / "component_count_avg.sparql",
            measure_ws / "component_count_min.sparql",
            measure_ws / "component_count_max.sparql",
            measure_ws / "choice_feature_count.sparql",
            measure_ws / "choice_feature_count_avg.sparql",
            measure_ws / "choice_feature_count_min.sparql",
            measure_ws / "choice_feature_count_max.sparql",
            measure_ws / "num_feature_count.sparql",
            measure_ws / "text_feature_count.sparql",
            measure_ws / "knowledge_count.sparql",
            measure_ws / "knowledge_feature_average.sparql",
            measure_ws / "knowledge_feature_min.sparql",
            measure_ws / "knowledge_feature_max.sparql",
            measure_ws / "inverse_knowledge_feature_average.sparql",
            measure_ws / "inverse_knowledge_feature_min.sparql",
            measure_ws / "inverse_knowledge_feature_max.sparql",
            measure_ws / "avg_terminology_depth.sparql"
            ]
        visualizer = RadarVisualizer()
        return visualizer.collect(self.inputfiles, measures)


def resolve_input_files(inputfiles: list[str] | None, directory: str | None) -> list[Path]:
    resolved_files: list[Path] = []

    if inputfiles:
        resolved_files.extend(Path(inputfile) for inputfile in inputfiles)

    if directory:
        input_directory = Path(directory)
        if not input_directory.is_dir():
            raise ValueError(f"Input directory does not exist or is not a directory: {input_directory}")

        directory_files = sorted(
            file_path
            for file_path in input_directory.iterdir()
            if file_path.is_file() and file_path.suffix.lower() in RDF_FILE_SUFFIXES
        )
        if not directory_files:
            raise ValueError(f"No RDF files found in directory: {input_directory}")

        resolved_files.extend(directory_files)

    unique_files: list[Path] = []
    seen_files: set[Path] = set()
    for file_path in resolved_files:
        normalized_path = file_path.resolve()
        if normalized_path not in seen_files:
            seen_files.add(normalized_path)
            unique_files.append(file_path)

    if not unique_files:
        raise ValueError("Provide at least one RDF input file with -i or a directory with -d.")

    return unique_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert COOM RDF files and collect measure data for radar visualization.")
    parser.add_argument("-i", "--inputfiles", help="Input COOM RDF files.", nargs="+")
    parser.add_argument("-d", "--directory", help="Directory containing RDF files to process.")
    return parser.parse_args()


def main() -> None:
    """Parse CLI arguments and run the radar-data collection pipeline."""
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    input_files = resolve_input_files(args.inputfiles, args.directory)
    app = COOMDescribe(input_files)
    radar_data = app.describe()
    print(radar_data)


if __name__ == "__main__":
    main()
