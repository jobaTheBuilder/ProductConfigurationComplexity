import unittest

from ResultPrinter import ResultPrinter


class ResultPrinterTest(unittest.TestCase):
    def test_print_formats_rows_as_markdown_table(self) -> None:
        printer = ResultPrinter()
        printer.add_row("choice_feature_count_as_str.sparql", "6")
        printer.add_row("knowledge_feature_average_as_str.sparql", "1.0")

        self.assertEqual(
            "\n".join(
                [
                    "| Measure                   | Value |",
                    "| ------------------------- | ----- |",
                    "| choice_feature_count      |     6 |",
                    "| knowledge_feature_average |     1 |",
                ]
            ),
            printer.print_as_markdown(),
        )


if __name__ == "__main__":
    unittest.main()
