import argparse
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

from COOM2AnalysisKnowledgeGraph import COOM2AnalysisKnowledgeGraph
from KGDescribe import KGDescribe


@dataclass
class RadarData:
    """Store measure values by measure name and knowledge-graph name."""

    values_by_measure: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def add_result(self, graph_name: str, measure_name: str, value: str) -> None:
        """Store one SPARQL result for one generated knowledge graph."""
        self.values_by_measure.setdefault(measure_name, {})[graph_name] = value

    def as_markdown_table(self) -> str:
        """Render the aggregated radar data as a Markdown table."""
        graph_names = sorted(
            {
                graph_name
                for values_by_graph in self.values_by_measure.values()
                for graph_name in values_by_graph
            }
        )
        headers = ["Measure", *graph_names]
        rows = []

        for measure_name in sorted(self.values_by_measure):
            values_by_graph = self.values_by_measure[measure_name]
            rows.append([measure_name, *[values_by_graph.get(graph_name, "") for graph_name in graph_names]])

        all_rows = [headers, *rows]
        widths = [
            max(len(str(row[column_index])) for row in all_rows)
            for column_index in range(len(headers))
        ]

        header_line = "| " + " | ".join(
            str(header).ljust(widths[index]) for index, header in enumerate(headers)
        ) + " |"
        separator_line = "| " + " | ".join("-" * width for width in widths) + " |"
        body_lines = [
            "| " + " | ".join(
                str(cell).ljust(widths[index]) for index, cell in enumerate(row)
            ) + " |"
            for row in rows
        ]

        return "\n".join([header_line, separator_line, *body_lines])

    def _graph_names(self) -> List[str]:
        return sorted(
            {
                graph_name
                for values_by_graph in self.values_by_measure.values()
                for graph_name in values_by_graph
            }
        )

    def _measure_names(self) -> List[str]:
        return sorted(self.values_by_measure)

    def _numeric_value(self, value: str) -> float:
        return float(str(value).strip())

    def save_radar_plot(self, output_file: Path) -> None:
        """Render the aggregated measure data as a radar plot PDF."""
        graph_names = self._graph_names()
        measure_names = self._measure_names()
        if not graph_names or not measure_names:
            raise ValueError("Cannot render a radar plot without graphs and measures.")

        numeric_values_by_measure = {
            measure_name: [
                self._numeric_value(self.values_by_measure[measure_name][graph_name])
                for graph_name in graph_names
            ]
            for measure_name in measure_names
        }

        normalized_values_by_graph = {graph_name: [] for graph_name in graph_names}
        for measure_name in measure_names:
            values = numeric_values_by_measure[measure_name]
            minimum = min(values)
            maximum = max(values)
            if np.isclose(minimum, maximum):
                normalized = [1.0] * len(values)
            else:
                normalized = [(value - minimum) / (maximum - minimum) for value in values]

            for graph_name, normalized_value in zip(graph_names, normalized):
                normalized_values_by_graph[graph_name].append(normalized_value)

        angles = np.linspace(0, 2 * np.pi, len(measure_names), endpoint=False)
        closed_angles = np.concatenate([angles, [angles[0]]])

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"polar": True})
        for graph_name in graph_names:
            values = normalized_values_by_graph[graph_name]
            closed_values = values + values[:1]
            ax.plot(closed_angles, closed_values, linewidth=2, label=graph_name)
            ax.fill(closed_angles, closed_values, alpha=0.1)

        ax.set_xticks(angles)
        ax.set_xticklabels(measure_names)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"])
        ax.set_title("Radar Plot of Normalized Measure Values", pad=30)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))

        fig.tight_layout()
        fig.savefig(output_file)
        plt.close(fig)


class RadarVisualizer:
    """Convert multiple RDF inputs and collect comparable measure values."""

    def collect(self, input_files: List[Path], measure_definitions: List[Path]) -> RadarData:
        """Convert all inputs, execute all measures, and return the aggregated data."""
        radar_data = RadarData()

        for input_file in input_files:
            converted_graph = input_file.parent / f"{input_file.stem}_analysis.ttl"
            logging.info("Converting COOM RDF file to %s", converted_graph)
            converter = COOM2AnalysisKnowledgeGraph(input_file)
            converter.export(converted_graph)

            logging.info("Collecting measures for %s", converted_graph)
            describer = KGDescribe()
            describer.load(converted_graph)
            measure_results = describer.run_measures(measure_definitions)

            for measure_name, value in measure_results.items():
                radar_data.add_result(converted_graph.stem, measure_name, value)

        return radar_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert COOM RDF files and collect measure data for radar visualization."
    )
    parser.add_argument("-i", "--inputfiles", help="Input COOM RDF files.", nargs="+", required=True)
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF file for the radar plot.",
        default="radar.pdf",
    )
    return parser.parse_args()


def main() -> None:
    """Parse CLI arguments and collect radar measure data for all input files."""
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    measure_ws = Path(__file__).parent / "resources" / "measures"
    measures = [
        measure_ws / "component_count.sparql",
        measure_ws / "component_count_avg.sparql",
        # measure_ws / "component_count_min.sparql",
        # measure_ws / "component_count_max.sparql",
        measure_ws / "choice_feature_count.sparql",
        measure_ws / "choice_feature_count_avg.sparql",
        # measure_ws / "choice_feature_count_min.sparql",
        # measure_ws / "choice_feature_count_max.sparql",
        measure_ws / "num_feature_count.sparql",
        measure_ws / "text_feature_count.sparql",
        measure_ws / "knowledge_count.sparql",
        measure_ws / "knowledge_feature_average.sparql",
        # measure_ws / "knowledge_feature_min.sparql",
        # measure_ws / "knowledge_feature_max.sparql",
        # measure_ws / "inverse_knowledge_feature_average.sparql",
        # measure_ws / "inverse_knowledge_feature_min.sparql",
        # measure_ws / "inverse_knowledge_feature_max.sparql",
        # measure_ws / "avg_terminology_depth.sparql",
    ]
    visualizer = RadarVisualizer()
    radar_data = visualizer.collect([Path(inputfile) for inputfile in args.inputfiles], measures)
    radar_data.save_radar_plot(Path(args.output))
    print(radar_data.as_markdown_table())


if __name__ == "__main__":
    main()
