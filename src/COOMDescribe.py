import argparse
import logging
from pathlib import Path

from RadarVisualizer import RadarVisualizer


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert COOM RDF files and collect measure data for radar visualization.")
    parser.add_argument("-i", "--inputfiles", help="Input COOM RDF files.", nargs="+", required=True)
    return parser.parse_args()


def main() -> None:
    """Parse CLI arguments and run the radar-data collection pipeline."""
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    app = COOMDescribe([Path(inputfile) for inputfile in args.inputfiles])
    radar_data = app.describe()
    print(radar_data)


if __name__ == "__main__":
    main()
