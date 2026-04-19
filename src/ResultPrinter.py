from typing import List, Tuple


class ResultPrinter:
    def __init__(self) -> None:
        self.rows: List[Tuple[str, str]] = []

    def add_row(self, left: str, right: str) -> None:
        """Append one measure result row to the output table."""
        self.rows.append((left, right))

    def print_as_markdown(self) -> str:
        """Return all collected rows as a Markdown-style table."""
        headers = ("Measure", "Value")
        printable_rows = [
            (self._format_measure(left), self._format_value(right))
            for left, right in self.rows
        ]
        all_rows = [headers, *printable_rows]
        widths = [max(len(row[index]) for row in all_rows) for index in range(2)]

        lines = [
            f"| {headers[0].ljust(widths[0])} | {headers[1].rjust(widths[1])} |",
            f"| {'-' * widths[0]} | {'-' * widths[1]} |",
        ]
        for left, right in printable_rows:
            lines.append(f"| {left.ljust(widths[0])} | {right.rjust(widths[1])} |")

        return "\n".join(lines)

    def _format_measure(self, measure: str) -> str:
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
