from pathlib import Path
import unittest


try:
    from rdflib import Graph
except ImportError:  # pragma: no cover - depends on local environment
    Graph = None


class FeatureChoiceCountRegressionTest(unittest.TestCase):
    def test_excludes_textual_and_numerical_ranges(self) -> None:
        if Graph is None:
            self.skipTest("rdflib is not installed")

        root = Path(__file__).resolve().parents[1]
        graph = Graph()
        graph.parse(root / "resources" / "examples" / "coom_minfull_example_analysis.ttl", format="turtle")
        query = (root / "resources" / "measures" / "feature_choice_count.sparql").read_text(
            encoding="utf-8"
        )

        rows = list(graph.query(query))

        self.assertEqual(1, len(rows))
        self.assertEqual(3.5, rows[0]["count"].toPython())


if __name__ == "__main__":
    unittest.main()
