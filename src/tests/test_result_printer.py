import unittest

from ResultPrinter import ResultPrinter


class ResultPrinterTest(unittest.TestCase):
    def test_print_formats_rows_as_markdown_table_using_measure_names(self) -> None:
        printer = ResultPrinter()
        printer.add_row("Choice Feature Count", "6", "example_a")
        printer.add_row("Choice Feature Count", "8", "example_b")
        printer.add_row("Knowledge Feature Average", "1.0", "example_a")
        printer.add_row("Knowledge Feature Average", "2.25", "example_b")

        self.assertEqual(
            "\n".join(
                [
                    "| Measure                   | example_a | example_b |",
                    "| ------------------------- | --------- | --------- |",
                    "| Choice Feature Count      |         6 |         8 |",
                    "| Knowledge Feature Average |       1.0 |      2.25 |",
                ]
            ),
            printer.print_as_markdown(),
        )

    def test_print_trims_wrapping_parentheses_from_measure_names(self) -> None:
        printer = ResultPrinter()
        printer.add_row("(Choice Feature Count)", "6", "example_a")

        self.assertEqual(
            "\n".join(
                [
                    "| Measure              | example_a |",
                    "| -------------------- | --------- |",
                    "| Choice Feature Count |         6 |",
                ]
            ),
            printer.print_as_markdown(),
        )


if __name__ == "__main__":
    unittest.main()
