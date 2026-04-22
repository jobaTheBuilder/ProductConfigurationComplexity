from __future__ import annotations

from typing import Dict, List


class ResultPrinter:
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
        """Return all collected rows as a LaTeX tabular."""
        headers, printable_rows = self._build_printable_rows()
        alignments = ["l", *(["r"] * len(self.columns))]

        header_line = " & ".join(
            rf"\textbf{{{self._escape_latex(header)}}}" for header in headers
        ) + r" \\"
        body_lines = [
            " & ".join(
                self._format_latex_cell(cell, column_index)
                for column_index, cell in enumerate(row)
            ) + r" \\ \hline"
            for row in printable_rows
        ]

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

    def _format_value(self, value: str) -> str:
        try:
            numeric_value = float(value)
        except ValueError:
            return value

        return f"{round(numeric_value):,}"

    def _format_latex_cell(self, value: str, column_index: int) -> str:
        if column_index == 0:
            return self._escape_latex(str(value))

        try:
            numeric_value = float(value)
        except ValueError:
            return self._escape_latex(str(value))

        return f"{round(numeric_value):,}"

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
