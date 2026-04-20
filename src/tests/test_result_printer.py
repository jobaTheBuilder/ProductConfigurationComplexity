import unittest

from ResultPrinter import ResultPrinter


class ResultPrinterTest(unittest.TestCase):
    def test_print_formats_rows_as_markdown_table(self) -> None:
        printer = ResultPrinter()
        printer.add_row("choice_feature_count_as_str.sparql", "6", "example_a")
        printer.add_row("choice_feature_count_as_str.sparql", "8", "example_b")
        printer.add_row("knowledge_feature_average_as_str.sparql", "1.0", "example_a")
        printer.add_row("knowledge_feature_average_as_str.sparql", "2.25", "example_b")

        self.assertEqual(
            "\n".join(
                [
                    "| Measure                          | example_a | example_b |",
                    "| -------------------------------- | --------- | --------- |",
                    "| choice_feature_count_as_str      | 6         | 8         |",
                    "| knowledge_feature_average_as_str | 1.0       | 2.25      |",
                ]
            ),
            printer.print_as_markdown(),
        )


if __name__ == "__main__":
    unittest.main()
