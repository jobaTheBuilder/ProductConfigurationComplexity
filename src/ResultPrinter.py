from __future__ import annotations

import math
from typing import Dict, List

import matplotlib.pyplot as plt


class ResultPrinter:
    """Collects measure results and renders them as Markdown or LaTeX tables."""

    def __init__(self) -> None:
        self.columns: List[str] = []
        self.rows_by_measure: Dict[str, Dict[str, str]] = {}

    def add_row(self, measure: str, value: str, column: str = "Value") -> None:
        """Append one measure result cell to the output table."""
        if column not in self.columns:
            self.columns.append(column)
        self.rows_by_measure.setdefault(measure, {})[column] = value

    def print_as_markdown(self) -> str:
        """Return all collected rows as a Markdown-style table."""
        headers, printable_rows = self._build_printable_rows()

        all_rows = [headers, *printable_rows]
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
                str(cell).ljust(widths[index]) if index == 0 else str(cell).rjust(widths[index])
                for index, cell in enumerate(row)
            ) + " |"
            for row in printable_rows
        ]

        return "\n".join([header_line, separator_line, *body_lines])

    def print_as_latex(self) -> str:
        """Return all collected rows as LaTeX tabular."""
        headers, printable_rows = self._build_printable_rows()
        alignments = ["l", *(["r"] * len(self.columns))]

        header_line = " & ".join(
            rf"\textbf{{{self._escape_latex(header)}}}" for header in headers
        ) + r" \\"
        body_lines = []
        for row in printable_rows:
            numeric_values = [
                self._parse_numeric(cell)
                for cell in row[1:]
            ]
            max_value = max((value for value in numeric_values if value is not None), default=None)

            formatted_row = []
            for column_index, cell in enumerate(row):
                is_largest = (
                    column_index > 0
                    and max_value is not None
                    and self._parse_numeric(cell) == max_value
                )
                formatted_row.append(
                    self._format_latex_cell(cell, column_index, bold=is_largest)
                )
            body_lines.append(" & ".join(formatted_row) + r" \\ \hline")

        return "\n".join(
            [
                r"\begin{tabular}{" + "".join(alignments) + "}",
                r"\hline",
                header_line,
                r"\hline",
                *body_lines,
                r"\hline",
                r"\end{tabular}",
            ]
        )

    def print_netdiagram(self, measures: List[str], output_path: str = "netdiagram.pdf") -> str:
        """Generate a radar/net diagram for selected measures across all knowledge-base columns."""
        if not measures:
            raise ValueError("At least one measure must be provided.")
        if not self.columns:
            raise ValueError("No columns available to plot.")

        selected_measures: List[str] = []
        normalized_rows: List[List[float]] = []

        for requested_measure in measures:
            matching_key = next(
                (
                    key
                    for key in self.rows_by_measure
                    if self._format_measure(key) == requested_measure
                ),
                None,
            )
            if matching_key is None:
                raise ValueError(f"Unknown measure: {requested_measure}")

            parsed_values = []
            for column in self.columns:
                raw_value = self.rows_by_measure[matching_key].get(column, "")
                numeric = self._parse_numeric(raw_value)
                parsed_values.append(numeric if numeric is not None else 0.0)

            smoothed_values = [math.log1p(value) for value in parsed_values]
            row_min = min(smoothed_values)
            row_max = max(smoothed_values)
            if row_max == row_min:
                normalized = [0.0 for _ in smoothed_values]
            else:
                normalized = [
                    (value - row_min) / (row_max - row_min)
                    for value in smoothed_values
                ]

            selected_measures.append(requested_measure)
            normalized_rows.append(normalized)

        with plt.rc_context({"font.family": "Libertinus Sans"}):
            figure, axis = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
            angles = [2 * math.pi * i / len(selected_measures) for i in range(len(selected_measures))]
            closed_angles = [*angles, angles[0]]

            for column_index, column in enumerate(self.columns):
                series = [row[column_index] for row in normalized_rows]
                closed_series = [*series, series[0]]
                axis.plot(closed_angles, closed_series, label=column)
                axis.fill(closed_angles, closed_series, alpha=0.1)

            axis.set_xticks(angles)
            axis.set_xticklabels(selected_measures)
            axis.set_ylim(0, 1)
            axis.set_title("Normalized Net Diagram")
            axis.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))

            figure.tight_layout()
            figure.savefig(output_path)
            plt.close(figure)
        return output_path

    def _build_printable_rows(self) -> tuple[List[str], List[List[str]]]:
        headers = ["Measure", *self.columns]
        printable_rows = []
        for measure in self.rows_by_measure:
            row = [self._format_measure(measure)]
            for column in self.columns:
                raw_value = self.rows_by_measure[measure].get(column, "")
                row.append(self._format_value(raw_value) if raw_value else "")
            printable_rows.append(row)
        return headers, printable_rows

    @staticmethod
    def _format_measure(measure: str) -> str:
        if measure.startswith("\""):
            measure = measure[1:]
        if measure.endswith("\""):
            measure = measure[:-1]
        return measure

    @staticmethod
    def _format_value(value: str) -> str:
        try:
            numeric_value = float(value)
        except ValueError:
            return value

        return f"{round(numeric_value):,}"

    def _format_latex_cell(self, value: str, column_index: int, bold: bool = False) -> str:
        if column_index == 0:
            escaped_value = self._escape_latex(str(value))
            return rf"\textbf{{{escaped_value}}}" if bold else escaped_value

        numeric_value = self._parse_numeric(value)
        if numeric_value is None:
            escaped_value = self._escape_latex(str(value))
            return rf"\textbf{{{escaped_value}}}" if bold else escaped_value

        formatted_value = f"{round(numeric_value):,}"
        return rf"\textbf{{{formatted_value}}}" if bold else formatted_value

    @staticmethod
    def _parse_numeric(value: str) -> float | None:
        try:
            return float(str(value).replace(",", ""))
        except ValueError:
            return None

    @staticmethod
    def _escape_latex(value: str) -> str:
        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        return "".join(replacements.get(char, char) for char in value)
