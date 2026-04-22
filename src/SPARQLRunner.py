from __future__ import annotations

import argparse
from pathlib import Path

try:
    from rdflib import Graph
except ImportError:  # pragma: no cover - depends on local environment
    Graph = None

from MeasureSettings import MeasureSettings


class SPARQLRunner:
    def __init__(self, syntax: str = "turtle") -> None:
        if Graph is None:
            raise ImportError("rdflib is required to run SPARQL queries")
        self.syntax = syntax
        self.graph = Graph()

    def load_graph(self, graph_file: Path) -> None:
        self.graph = Graph()
        self.graph.parse(graph_file, format=self.syntax)

    def run_query(self, query_file: Path):
        query = query_file.read_text(encoding="utf-8")
        return self.graph.query(query)

    @staticmethod
    def format_results(results) -> str:
        if results.type != "SELECT":
            return str(results)

        variables = [str(variable) for variable in results.vars]
        rows = [variables]
        for row in results:
            rows.append([str(row[variable].toPython()) for variable in results.vars])

        widths = [
            max(len(row[column_index]) for row in rows)
            for column_index in range(len(variables))
        ]

        header = "| " + " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(rows[0])
        ) + " |"
        separator = "| " + " | ".join("-" * width for width in widths) + " |"
        body = [
            "| " + " | ".join(
                value.ljust(widths[index]) for index, value in enumerate(row)
            ) + " |"
            for row in rows[1:]
        ]

        return "\n".join([header, separator, *body])

    def execute(self, graph_file: Path, query_file: Path) -> str:
        self.load_graph(graph_file)
        results = self.run_query(query_file)
        return self.format_results(results)

    def execute_settings(self, graph_file: Path, settings_file: Path) -> str:
        self.load_graph(graph_file)
        measure_definitions = MeasureSettings(str(settings_file)).load_measure_definitions()
        outputs = []
        for measure_definition in measure_definitions:
            results = self.run_query(measure_definition.path)
            outputs.append(f"## {measure_definition.name}\n{self.format_results(results)}")
        kbdf = '# ' + str(graph_file) + '\n\n'
        return kbdf + "\n\n".join(outputs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SPARQL query files against one RDF graph.")
    parser.add_argument("-g", "--graph", required=True, help="Input RDF graph file.")
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("-q", "--query", help="SPARQL query file to execute.")
    query_group.add_argument(
        "-s",
        "--settings",
        help="YAML settings file listing SPARQL measures to execute.",
    )
    parser.add_argument(
        "--syntax",
        default="turtle",
        help="RDF syntax of the input graph. Defaults to turtle.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runner = SPARQLRunner(syntax=args.syntax)
    if args.settings:
        output = runner.execute_settings(Path(args.graph), Path(args.settings))
    else:
        output = runner.execute(Path(args.graph), Path(args.query))
    print(output)


if __name__ == "__main__":
    main()
