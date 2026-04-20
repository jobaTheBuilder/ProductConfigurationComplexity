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
        headers = ["Measure", *self.columns]
        printable_rows = []
        for measure in self.rows_by_measure:
            row = [self._format_measure(measure)]
            for column in self.columns:
                raw_value = self.rows_by_measure[measure].get(column, "")
                row.append(self._format_value(raw_value) if raw_value else "")
            printable_rows.append(row)

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

    @staticmethod
    def _format_measure(measure: str) -> str:
        if measure.endswith(".sparql"):
            return measure[:-7]
        return measure

    def _format_value(self, value: str) -> str:
        try:
            numeric_value = float(value)
        except ValueError:
            return value

        if numeric_value.is_integer():
            return value

        return f"{numeric_value:.2f}"
