from io import StringIO
import sys
import unittest

from ResultPrinter import ResultPrinter


class ResultPrinterTest(unittest.TestCase):
    def test_print_formats_rows_as_markdown_table(self) -> None:
        printer = ResultPrinter()
        printer.add_row("choice_feature_count.sparql", "6")
        printer.add_row("knowledge_feature_average.sparql", "1.0")

        stdout = sys.stdout
        buffer = StringIO()
        try:
            sys.stdout = buffer
            printer.print()
        finally:
            sys.stdout = stdout

        self.assertEqual(
            "\n".join(
                [
                    "| Measure                   | Value |",
                    "| ------------------------- | ----- |",
                    "| feature_count             | 6     |",
                    "| knowledge_feature_average | 1.0   |",
                ]
            )
            + "\n",
            buffer.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
